# Monte Carlo Fantasy Football Draft Simulator Featuring Pydantic

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![Pydantic v2](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/5697b1e4c4a9790ece607654e6c02a160620c7e1/docs/badge/v2.json)](https://pydantic.dev)

## How Does The Simulator Work?

In previous fantasy football drafts, I have struggled to pick the right players. At the start, I sometimes pick players whose point projections are not dramatically different than the projections of players who are still available in later rounds. At the end, I fail to pick backups for my players who are at the most risk of injury.

This program is my attempt to solve both of those problems. To better estimate whether a player is especially valuable in a given round, a Monte Carlo simulation uses a logistic regression of historical draft data to guess which players will be available in later rounds of the draft, ensuring that I never pick a player who is easily replaceable. And to more accurately anticipate which players need strong backups (not streamers), this program randomly assigns injuries and other setbacks to players, based on historical data, so I always load up on talented individuals in my most at-risk positions.

## Why Does The Simulator Use Pydantic Models?

[Pydantic](https://docs.pydantic.dev/latest/) models enable complex validation logic for Python classes and can be imported for use in [FastAPI](https://fastapi.tiangolo.com/) routes. Originally, I intended this simulator to be a full FastAPI backend, but as the program developed, my personal use case (for the 2024 draft year, anyways) was largely solved with inputs from the command line.

In the future, I may build a full backend (with these Pydantic models) and frontend to help other users complete their drafts. But first, I'll see how well the simulator performs during the 2024 season...

## Running The Simulator

Fork this repository, create a virtual environment, and run the main function:

```console
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3.12 main.py
```

To correctly return results for your league, you'll need to edit a couple of files in `data/`:

- draft_projections.csv
- historical_drafts.csv
- historical_projections.csv
- league_teams.csv

### Draft Projections File

This file includes player names, positions, and projected points for the current draft season from any resource you choose, like [The Athletic](https://www.nytimes.com/athletic/5475262/2024/05/29/2024-fantasy-football-cheat-sheet-generator-customizable-rankings-and-projections-tool/). The projected points should be tuned to your specific league's settings.

The following columns are required:

- Season
- Player
- Pos
- Team
- Projected FFP

### Historical Projections

Like `draft_projections.csv`, this file should include player names, positions, and projected points but for previous seasons. Additionally, it should include a column that tallies the actual number of points a player scored in that year.

The following columns are required:

- Season
- Player
- Pos
- Team
- Projected FFP
- Actual FFP (should be empty for the current draft year)

### Historical Drafts

This file informs the logistic regression that models how other teams in your league are predicted to pick. Ideally, it should be a reformatted download of your league's draft history.

The following columns are required:

- Pick
- Pos

### League Teams

This file provides the details for the league. Other information, like whether the simulation should replicate a snake draft, is contained within the `.env` file, which is read by `models/config.py`.

The following columns are required:

- Name
- Order (draft order)
- Owner
- Simulator (True/False or 1/0)

Technically, more than one team may be the simulator – or be owned by the user executing the program - allowing the user to test every pick of the draft.

## Sample Results

For each pick in which the simulating team is not drafting, the program will ask the user to input opponents' selections:

```console
ROUND 1, PICK 3
Team 3 is on the clock!
Whom did Team 3 draft? Jonathan Taylor
Team 3 selected Jonathan Taylor.
```

When the simulating team is drafting, the program will run as many Monte Carlo simulations of the draft as it can within its specified time period (which defaults to 30 seconds). Then, it will report the average amount of points the simulating team is expected to gain, given the drafting of the best player at each position, exluding kickers and defenses until round 7.

```console
ROUND 2, PICK 14
Team 1 is on the clock!
Running Monte Carlo simulation for Team 1...
This simulation will take approximately 30 seconds.
Simulated 100 drafts in 9.52 seconds.
Simulated 200 drafts in 18.83 seconds.
Simulated 300 drafts in 28.42 seconds.
Simulated 327 drafts in 30.00 seconds.
Average simulation points when selecting a QB: 1545.33
Average simulation points when selecting a RB: 1568.00
Average simulation points when selecting a WR: 1598.15
Average simulation points when selecting a TE: 1563.88
The best position to draft is WR.
The best player to draft is Mike Evans.
Whom did Team 1 draft? Mike Evans
Team 1 selected Mike Evans.
```

You don't need to select the player the program recommends. In fact, there's a small (but not zero) chance that it may make a horrible recommendation, because randomness plays a role in both its calculations of player points and projections of other teams' draft selections. Simply type the name of the player you actually selected, and the program will accept its mistake and carry on as usual.

## Contributing

The program is ready for 2024 fantasy football drafts, but it is still a work in progress. If you find it valuable but notice bugs, need changes, or require additional features, [open an issue](https://github.com/joewlos/activitypubdantic/issues) or fork to [start a PR](https://github.com/joewlos/activitypubdantic/pulls).

The `requirements.txt` file includes all of the packages your virtual environment needs, including `black` for formatting.

Thank you for your interest, and good luck in your draft!
