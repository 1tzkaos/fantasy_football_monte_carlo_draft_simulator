# -*- coding: utf-8 -*-
"""
PYDANTIC MODELS FOR PLAYERS
"""
from .config import DRAFT_YEAR, MAX_RANDOM_ADJUSTMENT
from .position import PositionMaxPoints, PositionTierDistributions, PositionTiers
from pydantic import BaseModel, field_validator, model_validator
import random
from typing import Dict, List, Union

# Load the position tiers, determined by environment variables
pt = PositionTiers()


class PlayerPoints(BaseModel):
    """
    Projected vs. actual points for a single player,
    which must be calculated separately and placed on a CSV
    """

    projected_points: float
    actual_points: Union[float, None] = None  # Will be none for current draft year


class PlayerPointsRandomized(BaseModel):
    """
    Information about a random projection of points for a player,
    including the total adjustment to the original projection
    """

    randomized_points: int
    projected_points: int
    adjustment: float = 0
    exceeded_max: bool = False

    @field_validator("adjustment")
    @classmethod
    def validate_adjustment(cls, value) -> float:
        """
        For readability, limit float to only two decimals
        """
        return round(value, 2)


class Player(BaseModel):
    """
    Store all player information, with an added method for
    returning a randomized point projection, based on historical distributions
    """

    name: str
    position: str
    position_tier: str = (
        None  # DST & K do not have tiers, because they're very streamable
    )
    nfl_team: str  # Abbreviation, for current draft year
    points: Dict[int, PlayerPoints]  # Key is the year of the points
    drafted: bool = False

    @field_validator("position", "position_tier")
    @classmethod
    def validate_position(cls, value) -> str:
        """
        Ensure the position is lowercase
        """
        return value.lower()

    def randomized_points(
        self,
        distributions: PositionTierDistributions = PositionTierDistributions(),
        max_points: PositionMaxPoints = PositionMaxPoints(),
        max_points_adjustment: float = MAX_RANDOM_ADJUSTMENT,
        year: int = DRAFT_YEAR,
    ) -> PlayerPointsRandomized:
        """
        Return a random point projection for the player, if a distribution exists
        """
        output = {"projected_points": self.points[year].projected_points}

        # If the tier distribution is not available (DST & K), return the projected points
        tier_distribution = distributions.model_dump().get(self.position_tier, None)
        if not tier_distribution:
            output["randomized_points"] = output["projected_points"]

        # Randomly selection an adjustment from the distribution and apply it
        else:
            output["adjustment"] = random.choice(tier_distribution)
            output["randomized_points"] = round(
                self.points[year].projected_points * (1.0 + output["adjustment"])
            )

            # If the adjustment exceeds the max points, return the max points
            max_allowed = int(
                max_points.model_dump()[self.position.lower()]
                * (1 + max_points_adjustment)
            )
            if output["randomized_points"] > max_allowed:
                output["randomized_points"] = max_allowed
                output["exceeded_max"] = True

            # If the adjustment is somehow negative, return zero points
            # Zero points simulates an early season-ending injury (like 2023 Aaron Rodgers)
            elif output["randomized_points"] < 0:
                output["randomized_points"] = 0

        # Return the output as a PlayerPointsRandomized object
        return PlayerPointsRandomized(**output)


class Players(BaseModel):
    """
    Segment players into lists by position, and assign position tiers
    which are helpful for simulating randomness in draft outcomes
    """

    qb: List[Player] = []
    rb: List[Player] = []
    wr: List[Player] = []
    te: List[Player] = []
    dst: List[Player] = []
    k: List[Player] = []
    players: List[Player] = []
    years: List[int] = []

    @model_validator(mode="before")
    def assign_players_to_positions(cls, data):
        """
        Assign the player to the correct position and position tiers
        """
        if "players" in data:
            years = set()
            for player in data["players"]:
                years.update(player.points.keys())
                if player.position in data:
                    data[player.position].append(player)
                else:
                    data[player.position] = [player]
            data["years"] = sorted(list(years))

        # For each position, order the players by projected points
        # if the list is for the current draft
        positions = ["qb", "rb", "wr", "te", "dst", "k"]
        for year in data["years"]:
            for position_order in positions:
                if position_order in data:
                    data[position_order] = sorted(
                        data[position_order],
                        key=lambda x: x.points[year].projected_points,
                        reverse=True,
                    )

            # For each position tier, assign players to their tier
            for position_tier in positions:
                if position_tier not in pt.model_dump():
                    if position_tier in data:  # DST & K do not have tiers
                        for player in data[position_tier]:
                            player.position_tier = player.position

                # If the index is within the tier, assign the tier
                else:
                    tier = pt.model_dump()[position_tier]
                    if position_tier in data:
                        for i, player in enumerate(data[position_tier]):
                            if i < tier["1"]:
                                player.position_tier = f"{position_tier}1"
                            elif i < tier["2"]:
                                player.position_tier = f"{position_tier}2"
                            else:
                                player.position_tier = f"{position_tier}3"

        # Return the data
        return data
