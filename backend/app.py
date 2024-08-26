# -*- coding: utf-8 -*-
"""
MONTE CARLO FANTASY FOOTBALL DRAFT SIMULATOR BACKEND
"""
import csv
from fastapi import FastAPI, File, HTTPException, Response, UploadFile
from odmantic import AIOEngine, ObjectId
from sklearn.base import RegressorMixin
from sklearn.linear_model import LogisticRegression
from typing import List

from models.config import DRAFT_YEAR, ROUND_SIZE, SNAKE_DRAFT
from models.player import Player, Players, PlayerPoints
from models.position import PositionMaxPoints, PositionTierDistributions
from models.team import Draft, League, LogisticRegressionVariables, LeagueSimple, Team


# Metadata
tags_metadata = [
    {
        "name": "league",
        "description": "Leagues are the centralized setting, containing teams and players.",
    },
    {"name": "player", "description": "Draftable players in a league."},
    {
        "name": "historical_player",
        "description": "Historical players in a league, which determine position tier distributions.",
    },
    {
        "name": "historical_draft",
        "description": "Historical drafts in a league, which train the logistic regression model.",
    },
    {
        "name": "draft",
        "description": "Drafts are copies of leagues, which can simulate a round-by-round draft.",
    },
]


# Initialize app and engine
app = FastAPI(
    title="FF Monte Carlo Draft Simulator", version="0.0.1", openapi_tags=tags_metadata
)
engine = AIOEngine(
    database="fantasy-football",
)


# Helper functions
async def get_a_league_by_id(league_id: ObjectId) -> League:
    """
    Get a league by its ID
    """
    league = await engine.find_one(League, League.id == league_id)
    if not league:
        raise HTTPException(status_code=404, detail="League not found")
    return league


def create_max_points(
    players: Players, draft_year: str = str(DRAFT_YEAR)
) -> PositionMaxPoints:
    """
    Use the top player in each position to set max points
    (so that any outliers are not too extreme)
    """
    max_points = {}
    for position in ["qb", "rb", "wr", "te", "dst", "k"]:
        max_points[position] = max(
            [
                player.points[draft_year].projected_points
                for player in players.__getattribute__(position)
            ]
        )
    return PositionMaxPoints(**max_points)


def create_historical_distributions(
    players: Players, draft_year: str = str(DRAFT_YEAR)
) -> PositionTierDistributions:
    """
    Use the difference between historical performance and projections
    to create distributions for each position tier
    (replicating injuries, breakouts, and busts from the past)
    """
    distributions = {}
    for player in players.players:

        # Append or create the list for the position tier
        if player.position_tier not in distributions:
            distributions[player.position_tier] = []

        # For each year available in the player's points, get the percentage adjustment
        for year, points in player.points.items():
            if points.actual_points and int(year) < int(
                draft_year
            ):  # Only use historical data
                distributions[player.position_tier].append(
                    (points.actual_points - points.projected_points)
                    / points.projected_points
                )

    # Return the position tier distributions
    return PositionTierDistributions(**distributions)


def fit_logistic_regression_model(
    logistic_regression_variables: LogisticRegressionVariables,
) -> RegressorMixin:
    """
    Train the model for simulating opponent draft picks
    """
    try:
        draft_pick_model = LogisticRegression(max_iter=1000)
        draft_pick_model.fit(
            logistic_regression_variables.x, logistic_regression_variables.y
        )
    except:
        raise HTTPException(
            status_code=500, detail="Failed to train logistic regression model"
        )
    return draft_pick_model


# Routes
@app.post("/league", response_model=League, tags=["league"])
async def create_league(
    file: UploadFile = File(...),
    name: str = "Fantasy Football League",
):
    """
    Read data from a POSTed CSV file and create a league
    """
    data = csv.DictReader((await file.read()).decode("utf-8-sig").splitlines())
    teams = []
    for row in data:
        teams.append(
            Team(
                name=row["Name"],
                draft_order=row["Order"],
                owner=row["Owner"],
                simulator=row["Simulator"] == "True" or row["Simulator"] == 1,
            )
        )
    league = League(teams=teams, snake_draft=SNAKE_DRAFT, name=name)
    await engine.save(league)
    return league


@app.get("/league", response_model=List[LeagueSimple], tags=["league"])
async def get_leagues():
    """
    Get all leagues
    """
    leagues = await engine.find(League)
    return leagues


@app.get("/league/{league_id}", response_model=League, tags=["league"])
async def get_league(league_id: ObjectId):
    """
    Get a league by its ID
    """
    league = await get_a_league_by_id(league_id)
    return league


@app.delete("/league/{league_id}", tags=["league"])
async def delete_league(league_id: ObjectId):
    """
    Delete a league by its ID
    """
    league = await get_a_league_by_id(league_id)
    await engine.delete(league)
    return Response(status_code=204)


@app.post("/league/{league_id}/player", response_model=League, tags=["player"])
async def add_players_to_league(
    league_id: ObjectId,
    file: UploadFile = File(...),
):
    """
    Add current, draftable players to a league
    """
    league = await get_a_league_by_id(league_id)
    data = csv.DictReader((await file.read()).decode("utf-8-sig").splitlines())
    players = []
    for row in data:
        players.append(
            Player(
                name=row["Player"],
                position=row["Pos"],
                nfl_team=row["Team"],
                drafted=False,
                points={
                    str(row["Season"]): PlayerPoints(
                        projected_points=row["Projected FFP"],
                        actual_points=row.get("Actual FFP", None),
                    )
                },
            )
        )
    league.players = Players(players=players)

    # Set the max points for each position
    league.position_max_points = create_max_points(league.players)

    # Save and return the league
    await engine.save(league)
    return league


@app.get("/league/{league_id}/player", response_model=Players, tags=["player"])
async def get_players(league_id: ObjectId, draftable_only: bool = True):
    """
    Get all players in a league
    """
    league = await get_a_league_by_id(league_id)
    players = league.players

    # Before returning the data, filter out drafted players if requested
    if draftable_only:
        return Players(players=[player for player in players if not player.drafted])
    else:
        return players


@app.delete("/league/{league_id}/player", tags=["player"])
async def delete_players_from_league(league_id: ObjectId):
    """
    Delete all players from a league
    """
    league = await get_a_league_by_id(league_id)
    league.players = Players()
    await engine.save(league)
    return Response(status_code=204)


@app.get(
    "/league/{league_id}/player/{player_name}", response_model=Player, tags=["player"]
)
async def get_player(league_id: ObjectId, player_name: str):
    """
    Get a player by their name
    """
    league = await get_a_league_by_id(league_id)
    player = [player for player in league.players if player.name == player_name]
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player[0]


@app.post(
    "/league/{league_id}/historical_player",
    response_model=League,
    tags=["historical_player"],
)
async def add_historical_player_data_to_league(
    league_id: ObjectId, file: UploadFile = File(...)
):
    """
    Add historical players to a league to determine position tier distributions
    """
    league = await get_a_league_by_id(league_id)
    data = csv.DictReader((await file.read()).decode("utf-8-sig").splitlines())
    players = []
    for row in data:
        players.append(
            Player(
                name=row["Player"],
                position=row["Pos"],
                nfl_team=row["Team"],
                drafted=False,
                points={
                    str(row["Season"]): PlayerPoints(
                        projected_points=row["Projected FFP"],
                        actual_points=row.get("Actual FFP", None),
                    )
                },
            )
        )
    league.position_tier_distributions = create_historical_distributions(
        Players(players=players)
    )
    await engine.save(league)
    return league


@app.get(
    "/league/{league_id}/historical_player",
    response_model=PositionTierDistributions,
    tags=["historical_player"],
)
async def get_historical_player_data_from_league(league_id: ObjectId):
    """
    Get all historical player data from a league
    """
    league = await get_a_league_by_id(league_id)
    return league.position_tier_distributions


@app.delete(
    "/league/{league_id}/historical_player",
    tags=["historical_player"],
)
async def delete_historical_player_data_from_league(league_id: ObjectId):
    """
    Delete all historical player data from a league
    """
    league = await get_a_league_by_id(league_id)
    league.position_tier_distributions = PositionTierDistributions()
    await engine.save(league)
    return Response(status_code=204)


@app.post(
    "/league/{league_id}/historical_draft",
    response_model=League,
    tags=["historical_draft"],
)
async def add_historical_draft_data_to_league(
    league_id: ObjectId, file: UploadFile = File(...)
):
    """
    Add historical draft data to a league to train the logistic regression model
    """
    league = await get_a_league_by_id(league_id)
    data = csv.DictReader((await file.read()).decode("utf-8-sig").splitlines())
    x = []
    y = []
    for row in data:
        x.append(row["Pick"])
        y.append(row["Pos"])
    league.logistic_regression_variables = LogisticRegressionVariables(x=x, y=y)
    await engine.save(league)
    return league


@app.get(
    "/league/{league_id}/historical_draft",
    response_model=LogisticRegressionVariables,
    tags=["historical_draft"],
)
async def get_historical_draft_data_from_league(league_id: ObjectId):
    """
    Get all historical draft data from a league
    """
    league = await get_a_league_by_id(league_id)
    return league.logistic_regression_variables


@app.delete(
    "/league/{league_id}/historical_draft",
    tags=["historical_draft"],
)
async def delete_historical_draft_data_from_league(league_id: ObjectId):
    """
    Delete all historical draft data from a league
    """
    league = await get_a_league_by_id(league_id)
    league.logistic_regression_variables = LogisticRegressionVariables()
    await engine.save(league)
    return Response(status_code=204)


@app.post("/league/{league_id}/draft", response_model=Draft, tags=["draft"])
async def start_draft(league_id: ObjectId):
    """
    Start a draft for a league
    """
    league = await get_a_league_by_id(league_id)
    draft = Draft(league=league)
    await engine.save(draft)
    return draft
