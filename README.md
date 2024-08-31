# Monte Carlo Fantasy Football Draft Simulator

### Featuring FastAPI, NextUI, ODMantic, and Pydantic

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![Pydantic v2](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/5697b1e4c4a9790ece607654e6c02a160620c7e1/docs/badge/v2.json)](https://pydantic.dev)

## How Does The Simulator Work?

In previous fantasy football drafts, I have struggled to pick the right players. At the start, I selected players whose point projections are not dramatically different than the projections of players who are still available in later rounds. At the end, I failed to draft backups for players who are at the most risk of injury.

This program is my attempt to solve both of those problems. To better estimate whether a player is especially valuable in a given round, a Monte Carlo simulation uses a logistic regression of historical draft data to guess which players will be available in later rounds of the draft, ensuring that I never pick a player who is easily replaceable. And to more accurately anticipate which players need strong, rostered backups (not streamers), this program randomly assigns injuries and other setbacks to players, based on historical data, so I always load up on talented individuals in my most at-risk positions.

## Running The Simulator

To run the simulator without any edits to its code, you must have Docker installed on your machine.

Fork this repository, and then run:

```console
docker-compose up
```

To correctly return results for your league, you'll need to tune the variables in `backend/models/config.py` to your league's settings and create a couple of CSV files:

### Players File

This file includes player names, positions, and projected points for the current draft season from any resource you choose, like [The Athletic](https://www.nytimes.com/athletic/5475262/2024/05/29/2024-fantasy-football-cheat-sheet-generator-customizable-rankings-and-projections-tool/). The projected points should align with your league's scoring rules.

The following columns are required:

- Season
- Player
- Pos
- Team
- Projected FFP

### Historical Players

Like `players.csv`, this file should include player names, positions, and projected points for previous seasons. Additionally, it should include a column that tallies the actual number of points a player scored in that year.

The following columns are required:

- Season
- Player
- Pos
- Team
- Projected FFP
- Actual FFP

### Historical Drafts

This file informs the logistic regression that models how other teams in your league are predicted to pick. Ideally, it should be a reformatted download of your league's draft history for previous years. For example, [Sleeper](https://docs.sleeper.com/) provides an API for accessing draft histories.

The following columns are required:

- Pick
- Pos

### Teams

This file provides the details for your league. Other information, like whether the simulation should replicate a snake draft, should be contained within the `.env` file, which is read by `backend/models/config.py`.

The following columns are required:

- Name
- Order `(draft order)`
- Owner
- Simulator `(True/False or 1/0)`

Technically, more than one team may be the simulator – or be owned by the user executing the program - allowing the user to test every pick of the draft.

## Screenshots

The following screenshots are samples from the NextUI frontend.

## Contributing

The program is ready for 2024 fantasy football drafts, but it is still a work in progress. If you find it valuable but notice bugs, need changes, or require additional features, [open an issue](https://github.com/joewlos/fantasy_football_monte_carlo_draft_simulator/issues) or fork to [start a PR](https://github.com/joewlos/fantasy_football_monte_carlo_draft_simulator/pulls).

Thank you for your interest, and good luck in your draft!
