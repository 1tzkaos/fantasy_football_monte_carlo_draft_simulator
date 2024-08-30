# -*- coding: utf-8 -*-
"""
MONTE CARLO FANTASY FOOTBALL DRAFT SIMULATOR BACKEND
"""
import csv
from datetime import datetime
from fastapi import FastAPI, File, HTTPException, Response, UploadFile
from odmantic import AIOEngine, ObjectId
import random
from sklearn.base import RegressorMixin
from sklearn.linear_model import LogisticRegression
from starlette.middleware.cors import CORSMiddleware
from typing import List

from models.config import DRAFT_YEAR, SNAKE_DRAFT
from models.player import Player, Players, PlayerPoints
from models.position import PositionMaxPoints, PositionTierDistributions
from models.team import (
    Draft,
    DraftSimple,
    League,
    LogisticRegressionVariables,
    LeagueSimple,
    Team,
)


# Metadata
tags_metadata = [
    {
        "name": "league",
        "description": "Leagues are the centralized setting and must be initialized with a list of teams.",
    },
    {
        "name": "player",
        "description": "Draftable players in a league, with projections of their performance this season.",
    },
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


# Include origins for CORS
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1",
    "http://127.0.0.1:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
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


async def get_a_draft_by_id(draft_id: ObjectId) -> Draft:
    """
    Get a draft by its ID
    """
    draft = await engine.find_one(Draft, Draft.id == draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    return draft


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
        x = [[int(x)] for x in logistic_regression_variables.x]
        y = logistic_regression_variables.y
        draft_pick_model.fit(x, y)
    except:
        raise HTTPException(
            status_code=500, detail="Failed to train logistic regression model"
        )
    return draft_pick_model


def simulate_pick(
    league: League,
) -> str:
    """
    Simulate a pick using the logistic model to get probabilities for each position
    """
    players = league.players
    draft_pick_model = fit_logistic_regression_model(
        league.logistic_regression_variables
    )

    # Calculate the weights
    pick_number = league.current_draft_turn
    team_index = league.draft_order[pick_number]
    team = league.teams[team_index]
    weights = team.draft_turn_position_weights(pick_number + 1, draft_pick_model)
    weights = {k.lower(): v for k, v in weights.items()}

    # Randomly choose which position to pick, based on the weights
    positions = list(weights.keys())
    weights = list(weights.values())
    position_players = []
    while len(position_players) == 0:
        selection = random.choices(positions, weights=weights)[0]
        position_players = [
            x for x in getattr(players, selection) if x.drafted == False
        ]

        # If there are no players left in that position, remove it from the list
        if len(position_players) == 0:
            weights.remove(weights[positions.index(selection)])
            positions.remove(selection)

            # If the total weights are zero, reset them and just go random
            # (this can happen at the end of the draft)
            if sum(weights) == 0:
                weights = [1 for _ in positions]

    # Draft the best draftable player within that position
    player = position_players[0]
    return player.name


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
    league = League(
        teams=teams, snake_draft=SNAKE_DRAFT, name=name, created=datetime.now()
    )
    await engine.save(league)
    return league


@app.get("/league", response_model=List[LeagueSimple], tags=["league"])
async def get_leagues(ready_for_draft: bool = True):
    """
    Get all leagues (default to only leagues that are ready for a draft)
    """
    leagues = await engine.find(League)
    if ready_for_draft:
        leagues = [league for league in leagues if league.ready_for_draft]
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


@app.post("/league/{league_id}/draft", response_model=Draft, tags=["league"])
async def create_draft_for_a_league(league_id: ObjectId):
    """
    Start a draft for a league
    """
    league = await get_a_league_by_id(league_id)
    if not league.ready_for_draft:
        raise HTTPException(status_code=400, detail="League is not ready for a draft")
    draft = Draft(league=league, created=datetime.now())
    await engine.save(draft)
    return draft


@app.post("/league/{league_id}/player", response_model=League, tags=["player"])
async def add_players_to_league(
    league_id: ObjectId,
    file: UploadFile = File(...),
):
    """
    Add current, draftable players to a league
    """
    league = await get_a_league_by_id(league_id)
    if league.players.players:
        raise HTTPException(
            status_code=400, detail="Players already exist for this league"
        )

    # Read the CSV file and create players
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
    league.ready_position_max_points = True

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
    if league.ready_position_tier_distributions:
        raise HTTPException(
            status_code=400, detail="Historical players already exist for this league"
        )

    # Read the CSV file and create players
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
    league.ready_position_tier_distributions = True
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
    if (
        league.logistic_regression_variables.x
        and league.logistic_regression_variables.y
    ):
        raise HTTPException(
            status_code=400,
            detail="Historical draft data already exists for this league",
        )

    # Read the CSV file and create logistic regression variables
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


@app.get("/draft/{draft_id}", response_model=Draft, tags=["draft"])
async def get_draft(draft_id: ObjectId):
    """
    Get a draft by its ID
    """
    draft = await get_a_draft_by_id(draft_id)
    return draft


@app.get("/draft", response_model=List[DraftSimple], tags=["draft"])
async def get_drafts():
    """
    Get all drafts from leagues that exist
    """
    leagues = await engine.find(League)
    drafts = []
    for league in leagues:
        drafts += await engine.find(Draft, Draft.league == league.id)
    return drafts


@app.post("/draft/{draft_id}/pick", response_model=Draft, tags=["draft"])
async def make_draft_pick(
    draft_id: ObjectId, name: str = "", use_simulator: bool = False
):
    """
    Make a draft pick by name or using the simulator
    """
    draft = await get_a_draft_by_id(draft_id)
    league = draft.league
    if name and use_simulator:
        raise HTTPException(
            status_code=400, detail="Cannot include a name and use the simulator"
        )
    if not name and not use_simulator:
        raise HTTPException(
            status_code=400, detail="Must include a name or use the simulator"
        )

    # If using the simulator, get a pick name
    if use_simulator:
        name = simulate_pick(draft.league)

    # Find the player picked by name
    players = draft.league.players.players
    player = [player for player in players if player.name == name]
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    else:
        player = player[0]

    # Set the player as drafted within the league too
    position = player.position.lower()
    for k in ["players", position]:
        if hasattr(league.players, k):
            position_players = getattr(league.players, k)
            # Find the player in the list by name
            player_index = next(
                (
                    index
                    for index, player in enumerate(position_players)
                    if player.name == name
                ),
                None,
            )
            position_players[player_index].drafted = True

    # Draft the player
    player.drafted = True
    league.add_player_to_current_draft_turn_team(player)

    # Save the draft
    await engine.save(draft)

    # Return the draft after all operations have been performed
    return draft
