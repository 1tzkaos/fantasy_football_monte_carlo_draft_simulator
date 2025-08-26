#!/usr/bin/env python3
"""
HTML to CSV Parser for Fantasy Football Data
Parses HTML table data and appends it to existing CSV files.
"""

import os
import re
import csv
from bs4 import BeautifulSoup
from typing import List, Dict, Tuple, Optional


class FantasyFootballParser:
    def __init__(self):
        self.season = "2025"  # Default season
        
    def parse_html_file(self, html_file_path: str) -> List[Dict[str, str]]:
        """
        Parse HTML file containing fantasy football table data.
        
        Args:
            html_file_path: Path to HTML file
            
        Returns:
            List of dictionaries containing player data
        """
        try:
            with open(html_file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            players_data = []
            
            # Find all table rows with player data
            rows = soup.find_all('tr', {'data-player-row': True})
            
            for row in rows:
                player_data = self._extract_player_data(row)
                if player_data:
                    players_data.append(player_data)
            
            return players_data
            
        except Exception as e:
            print(f"Error parsing HTML file: {e}")
            return []
    
    def _extract_player_data(self, row) -> Optional[Dict[str, str]]:
        """
        Extract player data from a table row.
        
        Args:
            row: BeautifulSoup row element
            
        Returns:
            Dictionary with player data or None if extraction fails
        """
        try:
            # Extract player name
            name_element = row.find('a', class_='AnchorLink link clr-link pointer')
            if not name_element:
                return None
            player_name = name_element.get_text(strip=True)
            
            # Extract team and position
            team_element = row.find('span', class_='playerinfo__playerteam')
            pos_element = row.find('span', class_='playerinfo__playerpos')
            
            if not team_element or not pos_element:
                return None
                
            team = team_element.get_text(strip=True)
            position = pos_element.get_text(strip=True)
            
            # Extract fantasy points (last column with fantasy points)
            points_element = row.find('div', class_='jsx-2810852873 table--cell fw-bold tc total tc sorted')
            if not points_element:
                return None
                
            points_span = points_element.find('span')
            if not points_span:
                return None
                
            fantasy_points = points_span.get_text(strip=True)
            
            # Handle missing data - convert "--" to "0"
            fantasy_points = self._handle_missing_data(fantasy_points)
            
            # Convert team abbreviations to match existing data format
            team = self._normalize_team_name(team)
            
            return {
                'Season': self.season,
                'Player': player_name,
                'Pos': position,
                'Team': team,
                'Projected FFP': fantasy_points
            }
            
        except Exception as e:
            print(f"Error extracting player data from row: {e}")
            return None
    
    def _normalize_team_name(self, team: str) -> str:
        """
        Normalize team names to match existing CSV format.
        
        Args:
            team: Team abbreviation from HTML
            
        Returns:
            Normalized team abbreviation
        """
        team_mapping = {
            'Buf': 'BUF',
            'Chi': 'CHI', 
            'Dal': 'DAL',
            'NYJ': 'NYJ',
            'GB': 'GB',
            'LAC': 'LAC',
            'Atl': 'ATL',
            'Ind': 'IND',
            'NO': 'NO',
            # Add more mappings as needed
        }
        
        return team_mapping.get(team, team.upper())
    
    def append_to_csv(self, csv_file_path: str, players_data: List[Dict[str, str]]) -> bool:
        """
        Append player data to existing CSV file.
        
        Args:
            csv_file_path: Path to CSV file
            players_data: List of player dictionaries
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not players_data:
                print("No player data to append.")
                return False
            
            # Check if CSV file exists
            if not os.path.exists(csv_file_path):
                print(f"CSV file does not exist: {csv_file_path}")
                return False
            
            # Append data to CSV
            with open(csv_file_path, 'a', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Season', 'Player', 'Pos', 'Team', 'Projected FFP']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                for player in players_data:
                    writer.writerow(player)
            
            print(f"Successfully appended {len(players_data)} players to {csv_file_path}")
            return True
            
        except Exception as e:
            print(f"Error appending to CSV file: {e}")
            return False
    
    def get_user_file_selection(self, prompt: str, default_path: str = "") -> str:
        """
        Get file path from user input with validation.
        
        Args:
            prompt: Prompt message for user
            default_path: Default file path
            
        Returns:
            Valid file path
        """
        while True:
            if default_path:
                user_input = input(f"{prompt} (default: {default_path}): ").strip()
                if not user_input:
                    user_input = default_path
            else:
                user_input = input(f"{prompt}: ").strip()
            
            if os.path.exists(user_input):
                return user_input
            else:
                print(f"File not found: {user_input}")
                print("Please enter a valid file path.")
    
    def preview_data(self, players_data: List[Dict[str, str]], num_records: int = 5) -> None:
        """
        Preview parsed player data.
        
        Args:
            players_data: List of player dictionaries
            num_records: Number of records to preview
        """
        if not players_data:
            print("No data to preview.")
            return
        
        print(f"\nPreview of parsed data ({min(num_records, len(players_data))} of {len(players_data)} records):")
        print("-" * 80)
        
        for i, player in enumerate(players_data[:num_records]):
            print(f"{i+1}. {player['Player']} ({player['Pos']}, {player['Team']}) - {player['Projected FFP']} points")
        
        if len(players_data) > num_records:
            print(f"... and {len(players_data) - num_records} more records")
        print("-" * 80)


def main():
    """Main function to run the parser interactively."""
    parser = FantasyFootballParser()
    
    print("Fantasy Football HTML to CSV Parser")
    print("=" * 40)
    
    # Get HTML file path from user
    default_html = "/Users/nicholasstankiewicz/Documents/GitHub/fantasy_football_monte_carlo_draft_simulator/ranks-101-200.html"
    html_file_path = parser.get_user_file_selection(
        "Enter path to HTML file to parse", 
        default_html
    )
    
    # Parse HTML file
    print(f"\nParsing HTML file: {html_file_path}")
    players_data = parser.parse_html_file(html_file_path)
    
    if not players_data:
        print("No player data found in HTML file. Exiting.")
        return
    
    # Preview parsed data
    parser.preview_data(players_data)
    
    # Ask user if they want to proceed
    proceed = input(f"\nProceed with appending {len(players_data)} players? (y/N): ").strip().lower()
    if proceed != 'y':
        print("Operation cancelled.")
        return
    
    # Get CSV file path from user
    default_csv = "/Users/nicholasstankiewicz/Documents/GitHub/fantasy_football_monte_carlo_draft_simulator/data.csv"
    csv_file_path = parser.get_user_file_selection(
        "Enter path to CSV file to append to",
        default_csv
    )
    
    # Append data to CSV
    print(f"\nAppending data to CSV file: {csv_file_path}")
    success = parser.append_to_csv(csv_file_path, players_data)
    
    if success:
        print("✅ Data successfully appended to CSV file!")
    else:
        print("❌ Failed to append data to CSV file.")


if __name__ == "__main__":
    main()