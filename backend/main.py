# -*- coding: utf-8 -*-
"""
MONTE CARLO FANTASY FOOTBALL DRAFT SIMULATOR (COMMAND LINE VERSION)
"""
from models.config import DRAFT_YEAR, ROUND_SIZE, SNAKE_DRAFT
from models.player import Player, Players, PlayerPoints
from models.position import (
    PositionMaxPoints,
    PositionTierDistributions,
)
from models.team import Team, League
import pandas as pd
import random
from sklearn.base import RegressorMixin
from sklearn.linear_model import LogisticRegression
import time


"""
LOAD FROM CSVs
"""


def load_players(csv: str) -> Players:
    """
    Return a list of player objects from a CSV file with the following columns:
    - Season
    - Player
    - Pos
    - Team
    - Projected FFP
    - Actual FFP (should be empty for the current draft year)
    """
    data = pd.read_csv(csv).to_dict("records")
    all_players = []
    for row in data:
        all_players.append(
            Player(
                name=row["Player"],
                position=row["Pos"],
                nfl_team=row["Team"],
                drafted=False,
                points={
                    int(row["Season"]): PlayerPoints(
                        projected_points=row["Projected FFP"],
                        actual_points=row.get("Actual FFP", None),
                    )
                },
            )
        )
    return Players(players=all_players)


def load_teams(csv: str) -> League:
    """
    Return a list of team objects from a CSV file with the following columns:
    - Name
    - Order (draft order)
    - Owner
    - Simulator (True/False or 1/0)
    """
    data = pd.read_csv(csv).to_dict("records")
    all_teams = []
    for row in data:
        all_teams.append(
            Team(
                name=row["Name"],
                draft_order=row["Order"],
                owner=row["Owner"],
                simulator=row["Simulator"] == "True" or row["Simulator"] == 1,
            )
        )
    return League(teams=all_teams, snake_draft=SNAKE_DRAFT)


def load_logistic_regression_variables(csv: str) -> tuple:
    """
    Return x and y values for fitting a logistic regression model
    for predicting the position of a draft pick based on historical draft data
    from a CSV file with the following columns:
    - Pick
    - Pos
    """
    data = pd.read_csv(csv)
    x = data[["Pick"]]
    y = data["Pos"].str.lower()
    return x.values, y.values


"""
DISTRIBUTIONS AND MAX POINTS FOR RANDOM PROJECTIONS
"""


def create_max_points(
    players: Players, draft_year: int = DRAFT_YEAR
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
    players: Players, draft_year: int = DRAFT_YEAR
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
            if points.actual_points and year < draft_year:  # Only use historical data
                distributions[player.position_tier].append(
                    (points.actual_points - points.projected_points)
                    / points.projected_points
                )

    # Return the position tier distributions
    return PositionTierDistributions(**distributions)


"""
ACTIONS
"""


def draft_player(name: str, league: League, players: Players):
    """
    Draft a player by name and add them to the team that is currently selecting
    """
    player = [player for player in players.players if player.name == name]
    if player:
        if not player[0].drafted:
            raw_player = player[0].model_dump()
            raw_player["drafted"] = True
            player[0] = Player(**raw_player)
            league.add_player_to_current_draft_turn_team(player[0])
        else:
            raise ValueError(f"{name} has already been drafted.")
    return


def simulate_pick(
    league: League,
    players: Players,
    model: RegressorMixin,
    team_index: int,
    pick_number: int,
) -> str:
    """
    Simulate a pick using the logistic model to get probabilities for each position
    """
    team = league.teams[team_index]
    weights = team.draft_turn_position_weights(pick_number + 1, model)

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


def simulate_draft(league: League, players: Players, model: RegressorMixin):
    """
    Simulate an entire draft using the logistic model
    """
    draft_order = league.draft_order.copy()
    for i, team_index in enumerate(draft_order):
        player_name = simulate_pick(league, players, model, team_index, i)
        draft_player(player_name, league, players)
    return


def monte_carlo_draft(
    league: League,
    players: Players,
    max_points: PositionMaxPoints,
    distributions: PositionTierDistributions,
    model: RegressorMixin,
    seconds: float = 30,  # Set to whatever time is best for the draft
) -> dict:
    """
    Simulate drafts for each position and return the average points scored
    to determine which position is best to draft
    """
    simulator_team = [i for i, team in enumerate(league.teams) if team.simulator]
    results = {"qb": [], "rb": [], "wr": [], "te": []}
    if league.current_draft_turn > ROUND_SIZE * 7:  # Add DST & K after round 7
        results["dst"] = []
        results["k"] = []
    start_time = time.time()
    i = 0
    print(f"This simulation will take approximately {round(seconds, 2)} seconds.")
    while time.time() - start_time < seconds:
        for position in results.keys():
            i += 1
            league_copy = league.model_copy(deep=True)
            players_copy = players.model_copy(deep=True)
            possible_players = [
                player
                for player in players.__getattribute__(position)
                if player.drafted == False
            ]
            if len(possible_players) == 0:
                results[position].append(0)  # No players left
                continue
            best_player = possible_players[0]
            draft_player(best_player.name, league_copy, players_copy)
            simulate_draft(league_copy, players_copy, model)

            # Append the points for the simulator team
            results[position].append(
                league_copy.teams[simulator_team[0]].randomized_starter_points(
                    distributions=distributions, max_points=max_points
                )
            )
        if i % 100 == 0:
            print(
                f"Simulated {i} drafts in {round(time.time() - start_time, 2)} seconds."
            )
    print(f"Simulated {i} drafts in {round(seconds, 2)} seconds.")

    # Turn the arrays into averages
    for position in results.keys():
        results[position] = round(sum(results[position]) / len(results[position]), 2)
    return results


"""
EXECUTE FROM THE COMMAND LINE
"""


def main():
    data_error = 'Please make sure that the CSV files are in the "data" folder.'
    try:
        draft_players = load_players("data/draft_projections.csv")
        historical_players = load_players("data/historical_projections.csv")
        league = load_teams("data/personal_league_teams.csv")
    except:
        raise ValueError(f"Error while loading data. {data_error}")

    # Fit a logistic regression for predicting the position of a draft pick
    try:
        lr_x, lr_y = load_logistic_regression_variables("data/historical_drafts.csv")
        draft_pick_model = LogisticRegression(max_iter=1000)
        draft_pick_model.fit(lr_x, lr_y)
    except:
        raise ValueError(f"Error while fitting the regression model. {data_error}")

    # Max points and position tier distributions for random projections
    position_max_points = create_max_points(draft_players)
    position_tier_distributions = create_historical_distributions(historical_players)

    """
    INTRODUCTION
    """
    print("\nWELCOME TO THE FANTASY FOOTBALL MONTE CARLO DRAFT SIMULATOR!")
    print(f"In this league, there are {len(league.teams)} teams.")
    print(
        f"When your turn starts, a Monte Carlo simulation will help you decide which player you should pick."
    )
    print(f"Good luck!\n")

    """
    SHOULD THIS BE A SIMULATION?
    """
    use_simulator = None
    print(
        "For practice, you can use a logistic regression model to make picks for other teams."
    )
    print(
        "This allows you to speedily check the Monte Carlo simulation results for each round, before the actual draft."
    )
    while use_simulator not in ["y", "n"]:
        use_simulator = input(
            "Would you like to use the model, instead of inputting your opponents' picks? (y/n) "
        ).lower()

    """
    BEGIN DRAFT
    """
    print("\nBEGINNING THE DRAFT...\n")
    draft_order = league.draft_order.copy()
    for pick_number, i in enumerate(draft_order):
        print(
            f"ROUND {league.current_draft_turn // ROUND_SIZE + 1}, PICK {league.current_draft_turn % ROUND_SIZE + 1}"
        )
        print(f"{league.teams[i].name} is on the clock!")
        player_name = None
        if league.teams[i].simulator:

            # Run the Monte Carlo simulation for the round
            print(f"Running Monte Carlo simulation for {league.teams[i].name}...")
            result = monte_carlo_draft(
                league,
                draft_players,
                position_max_points,
                position_tier_distributions,
                draft_pick_model,
            )

            # Print the outcome of each result
            for position, points in result.items():
                print(
                    f"Average simulation points when selecting a {position.upper()}: {points}"
                )

            # Find out which player is best
            best_position = max(result, key=result.get)
            print(f"The best position to draft is {best_position.upper()}.")
            best_player = [
                player
                for player in draft_players.__getattribute__(best_position)
                if player.drafted == False
            ][0]
            print(f"The best player to draft is {best_player.name}.")

        # Else if the simulator is being use
        elif use_simulator == "y":
            player_name = simulate_pick(
                league, draft_players, draft_pick_model, i, pick_number
            )

        # Ask for who was actually drafted
        while player_name is None:
            player_input = input(f"Whom did {league.teams[i].name} draft? ")
            if player_input in [p.name for p in draft_players.players]:
                player_name = player_input
            else:
                print(f"{player_input} is not a valid player name. Please try again.")

        # Draft the player
        draft_player(player_name, league, draft_players)
        print(f"{league.teams[i].name} selected {player_name}.\n")

    # For each team, get the average of 1,000 randomized starter points to report results
    randomized_results = {}
    randomized_firsts = {}
    randomizations = 1000
    for team in league.teams:
        name = f"{team.name}"
        randomized_results[name] = []
        randomized_firsts[name] = 0
        for _ in range(randomizations):
            randomized_results[name].append(
                team.randomized_starter_points(
                    distributions=position_tier_distributions,
                    max_points=position_max_points,
                )
            )
    for i in range(randomizations):
        first = None
        points = 0
        for key in randomized_results.keys():
            if randomized_results[key][i] > points:
                points = randomized_results[key][i]
                first = key
        randomized_firsts[first] += 1
    print("FINAL RESULTS:")
    sorted_keys = sorted(
        randomized_results, key=lambda x: sum(randomized_results[x]), reverse=True
    )
    for i, team in enumerate(sorted_keys):
        points = round(sum(randomized_results[team]) / len(randomized_results[team]))
        firsts = int(randomized_firsts[team] / randomizations * 100)
        print(f"{i + 1}. {team} ({firsts}% first place finishes): {points} points")

    # End the simulator
    print(
        f"\nThe draft is complete! Thank you for using the Fantasy Football Monte Carlo Draft Simulator."
    )
    print("May the best team (your team) win.\n")
    return


# When the script is run, execute the main function
if __name__ == "__main__":
    main()
