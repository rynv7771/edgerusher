#!/usr/bin/env python3
"""
ESPN Data Extractor
Parses ESPN API responses and extracts relevant info for AI analysis
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional

class ESPNDataExtractor:
    """Extract and structure ESPN NFL data for AI processing"""
    
    def __init__(self, raw_data: Dict):
        self.raw_data = raw_data
        
    def get_all_games(self) -> List[Dict]:
        """Extract all games from scoreboard"""
        games = []
        
        for event in self.raw_data.get('events', []):
            game_data = self.extract_game_data(event)
            if game_data:
                games.append(game_data)
        
        return games
    
    def extract_game_data(self, event: Dict) -> Optional[Dict]:
        """Extract structured data for a single game"""
        
        try:
            competition = event['competitions'][0]
            competitors = competition['competitors']
            
            # Get home/away teams
            home_team = next((c for c in competitors if c['homeAway'] == 'home'), None)
            away_team = next((c for c in competitors if c['homeAway'] == 'away'), None)
            
            if not home_team or not away_team:
                return None
            
            # Extract odds if available
            odds_data = None
            if 'odds' in competition and len(competition['odds']) > 0:
                odds = competition['odds'][0]
                odds_data = {
                    'spread': odds.get('spread'),
                    'spread_details': odds.get('details'),
                    'over_under': odds.get('overUnder'),
                    'home_moneyline': odds.get('homeTeamOdds', {}).get('moneyLine'),
                    'away_moneyline': odds.get('awayTeamOdds', {}).get('moneyLine'),
                    'provider': odds.get('provider', {}).get('name')
                }
            
            # Build structured game data
            game_data = {
                'game_id': event['id'],
                'game_time': event['date'],
                'game_time_display': competition['status']['type'].get('detail', ''),
                'status': competition['status']['type']['state'],
                'week': self.raw_data.get('week', {}).get('number'),
                'season_year': self.raw_data.get('season', {}).get('year', 2025),
                
                # Home team
                'home_team': {
                    'id': home_team['team']['id'],
                    'name': home_team['team']['displayName'],
                    'abbreviation': home_team['team']['abbreviation'],
                    'record': home_team.get('records', [{}])[0].get('summary', 'N/A') if home_team.get('records') else 'N/A',
                    'score': home_team.get('score', '0')
                },
                
                # Away team
                'away_team': {
                    'id': away_team['team']['id'],
                    'name': away_team['team']['displayName'],
                    'abbreviation': away_team['team']['abbreviation'],
                    'record': away_team.get('records', [{}])[0].get('summary', 'N/A') if away_team.get('records') else 'N/A',
                    'score': away_team.get('score', '0')
                },
                
                # Venue
                'venue': {
                    'name': competition.get('venue', {}).get('fullName', 'TBD'),
                    'city': competition.get('venue', {}).get('address', {}).get('city', ''),
                    'state': competition.get('venue', {}).get('address', {}).get('state', ''),
                    'indoor': competition.get('venue', {}).get('indoor', False)
                },
                
                # Broadcast
                'broadcast': competition.get('broadcasts', [{}])[0].get('names', ['N/A'])[0] if competition.get('broadcasts') else 'N/A',
                
                # Odds
                'odds': odds_data,
                
                # Raw data for reference
                'raw_event': event
            }
            
            return game_data
            
        except (KeyError, IndexError, TypeError) as e:
            print(f"Error extracting game data: {e}")
            return None
    
    def prepare_for_ai(self, game_data: Dict) -> str:
        """Format game data as a clean text prompt for AI analysis"""
        
        home = game_data['home_team']
        away = game_data['away_team']
        odds = game_data.get('odds', {})
        
        prompt = f"""Analyze this NFL matchup:

GAME INFO:
{away['name']} ({away['record']}) @ {home['name']} ({home['record']})
Date: {game_data['game_time_display']}
Venue: {game_data['venue']['name']} ({game_data['venue']['city']}, {game_data['venue']['state']})
Indoor: {'Yes' if game_data['venue']['indoor'] else 'No'}
Broadcast: {game_data['broadcast']}

BETTING LINES:
"""
        
        if odds:
            prompt += f"""Spread: {odds.get('spread_details', 'N/A')}
Over/Under: {odds.get('over_under', 'N/A')}
Moneyline: {home['abbreviation']} {odds.get('home_moneyline', 'N/A')} / {away['abbreviation']} {odds.get('away_moneyline', 'N/A')}
Source: {odds.get('provider', 'N/A')}
"""
        else:
            prompt += "Odds not yet available\n"
        
        return prompt

def test_extractor():
    """Test the extractor with mock data"""
    
    print("="*60)
    print("ESPN DATA EXTRACTOR TEST")
    print("="*60)
    
    # Load mock data
    with open('mock_espn_data.json', 'r') as f:
        raw_data = json.load(f)
    
    extractor = ESPNDataExtractor(raw_data)
    games = extractor.get_all_games()
    
    print(f"\n✅ Extracted {len(games)} games\n")
    
    for i, game in enumerate(games, 1):
        print(f"\n{'='*60}")
        print(f"GAME {i}: {game['away_team']['name']} @ {game['home_team']['name']}")
        print(f"{'='*60}")
        
        print(f"\nStructured Data:")
        print(f"  Game ID: {game['game_id']}")
        print(f"  Week: {game['week']}")
        print(f"  Time: {game['game_time_display']}")
        print(f"  Status: {game['status']}")
        
        print(f"\n  Away: {game['away_team']['name']} ({game['away_team']['record']})")
        print(f"  Home: {game['home_team']['name']} ({game['home_team']['record']})")
        
        if game['odds']:
            print(f"\n  Odds:")
            print(f"    Spread: {game['odds']['spread_details']}")
            print(f"    O/U: {game['odds']['over_under']}")
            print(f"    ML: {game['home_team']['abbreviation']} {game['odds']['home_moneyline']} / {game['away_team']['abbreviation']} {game['odds']['away_moneyline']}")
        
        print(f"\n{'='*60}")
        print(f"AI PROMPT FORMAT:")
        print(f"{'='*60}")
        print(extractor.prepare_for_ai(game))
        
        # Save individual game data
        filename = f"game_{game['game_id']}.json"
        with open(filename, 'w') as f:
            json.dump(game, f, indent=2)
        print(f"\n💾 Saved to {filename}")

if __name__ == "__main__":
    test_extractor()
