# Fantasy Football HTML to CSV Parser

This script parses HTML table data containing fantasy football player rankings and appends the data to an existing CSV file.

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the script interactively:
```bash
python html_to_csv_parser.py
```

The script will prompt you for:
1. **HTML file path**: The path to the HTML file containing player data (defaults to `ranks-101-200.html`)
2. **CSV file path**: The path to the existing CSV file to append data to (defaults to `data.csv`)

## Features

- **Interactive file selection**: Choose which files to parse and append to
- **Data validation**: Checks file existence and data integrity
- **Preview functionality**: Shows a preview of parsed data before appending
- **Error handling**: Comprehensive error handling with informative messages
- **Team name normalization**: Handles different team abbreviation formats

## Expected HTML Format

The script expects HTML table data with the following structure:
- Player rows with `data-player-row` attribute
- Player name in `<a class="AnchorLink link clr-link pointer">`
- Team in `<span class="playerinfo__playerteam">`
- Position in `<span class="playerinfo__playerpos">`
- Fantasy points in `<span>` within a div with class containing "total tc sorted"

## Expected CSV Format

The script appends data in the following CSV format:
```csv
Season,Player,Pos,Team,Projected FFP
2025,Player Name,WR,TEAM,123.4
```

## Example Output

```
Fantasy Football HTML to CSV Parser
========================================
Enter path to HTML file to parse (default: /path/to/ranks-101-200.html): 

Parsing HTML file: /path/to/ranks-101-200.html

Preview of parsed data (5 of 100 records):
--------------------------------------------------------------------------------
1. Ricky Pearsall (WR, SF) - 186.3 points
2. Keon Coleman (WR, BUF) - 180.8 points
3. Justin Herbert (QB, LAC) - 283.5 points
4. Caleb Williams (QB, CHI) - 280.4 points
5. Dak Prescott (QB, DAL) - 285.7 points
... and 95 more records
--------------------------------------------------------------------------------

Proceed with appending 100 players? (y/N): y
Enter path to CSV file to append to (default: /path/to/data.csv): 

Appending data to CSV file: /path/to/data.csv
Successfully appended 100 players to /path/to/data.csv
✅ Data successfully appended to CSV file!
```

## Notes

- The script automatically sets the season to 2025
- Team abbreviations are normalized to match common formats
- The script will not overwrite existing data, only append new records
- Make sure the target CSV file exists before running the script