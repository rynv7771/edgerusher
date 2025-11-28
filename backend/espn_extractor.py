#!/usr/bin/env python3
"""
Enhanced ESPN Data Extractor
Extracts comprehensive game data including team leaders and stats
"""

import json
from typing import Dict, List, Optional

class ESPNDataExtractor:
    """Extract and structure NFL game data from ESPN API"""
    
    def __init__(self, raw_data: Dict):
        self.raw_data = raw_data
    
    def get_all_games(self) -> List[Dict]:
        """Extract all games from the scoreboard"""
        games = []
        
        for event in self.raw_data.get('events', []):
            game = self._extract_game(event)
            if game:
                games.append(game)
        
        return games
    
    def _extract_game(self, event: Dict) -> Optional[Dict]:
        """Extract a single game with enhanced data"""
        
        try:
            competition = event['competitions'][0]
            competitors = competition['competitors']
            
            # Determine home/away
            home_team = next(c for c in competitors if c['homeAway'] == 'home')
            away_team = next(c for c in competitors if c['homeAway'] == 'away')
            
            # Extract team data with leaders
            home_data = self._extract_team_data(home_team)
            away_data = self._extract_team_data(away_team)
            
            # Extract odds
            odds = self._extract_odds(competition)
            
            return {
                'game_id': event['id'],
                'game_time': event['date'],
                'game_time_display': competition['status']['type'].get('detail', ''),
                'status': competition['status']['type']['state'],
                'week': self.raw_data.get('week', {}).get('number'),
                'season_year': self.raw_data.get('season', {}).get('year', 2025),
                
                'home_team': home_data,
                'away_team': away_data,
                
                'venue': {
                    'name': competition.get('venue', {}).get('fullName', 'TBD'),
                    'city': competition.get('venue', {}).get('address', {}).get('city', ''),
                    'state': competition.get('venue', {}).get('address', {}).get('state', ''),
                    'indoor': competition.get('venue', {}).get('indoor', False)
                },
                
                'broadcast': competition.get('broadcasts', [{}])[0].get('names', ['TBD'])[0] if competition.get('broadcasts') else 'TBD',
                
                'odds': odds
            }
            
        except Exception as e:
            print(f"Error extracting game: {e}")
            return None
    
    def _extract_team_data(self, competitor: Dict) -> Dict:
        """Extract enhanced team data including leaders"""
        
        team = competitor['team']
        records = competitor.get('records', [])
        
        # Get overall record
        overall_record = next((r['summary'] for r in records if r.get('type') == 'total'), 'N/A')
        home_record = next((r['summary'] for r in records if r.get('type') == 'home'), 'N/A')
        away_record = next((r['summary'] for r in records if r.get('type') == 'road'), 'N/A')
        
        # Extract team leaders
        leaders = self._extract_leaders(competitor.get('leaders', []))
        
        return {
            'id': team['id'],
            'name': team['displayName'],
            'abbreviation': team['abbreviation'],
            'record': overall_record,
            'home_record': home_record,
            'away_record': away_record,
            'score': competitor.get('score', '0'),
            'leaders': leaders
        }
    
    def _extract_leaders(self, leaders_data: List[Dict]) -> Dict:
        """Extract team statistical leaders"""
        
        leaders = {}
        
        for category in leaders_data:
            category_name = category['name']
            
            if category_name == 'passingLeader' and category.get('leaders'):
                leader = category['leaders'][0]
                leaders['passing'] = {
                    'player': leader['athlete']['displayName'],
                    'stats': leader['displayValue']
                }
            
            elif category_name == 'rushingLeader' and category.get('leaders'):
                leader = category['leaders'][0]
                leaders['rushing'] = {
                    'player': leader['athlete']['displayName'],
                    'stats': leader['displayValue']
                }
            
            elif category_name == 'receivingLeader' and category.get('leaders'):
                leader = category['leaders'][0]
                leaders['receiving'] = {
                    'player': leader['athlete']['displayName'],
                    'stats': leader['displayValue']
                }
        
        return leaders
    
    def _extract_odds(self, competition: Dict) -> Optional[Dict]:
        """Extract betting odds"""
        
        try:
            odds_data = competition.get('odds', [])
            if not odds_data:
                return None
            
            odds = odds_data[0]
            
            return {
                'provider': odds.get('provider', {}).get('name', 'Unknown'),
                'spread': odds.get('details', 'N/A'),
                'spread_details': odds.get('details', 'N/A'),
                'over_under': odds.get('overUnder', 'N/A'),
                'home_moneyline': odds.get('homeTeamOdds', {}).get('moneyLine', 'N/A'),
                'away_moneyline': odds.get('awayTeamOdds', {}).get('moneyLine', 'N/A')
            }
        
        except Exception:
            return None
    
    def prepare_for_ai(self, game_data: Dict) -> str:
        """Format game data for AI consumption"""
        
        home = game_data['home_team']
        away = game_data['away_team']
        odds = game_data.get('odds', {})
        
        prompt = f"""GAME DATA:
{away['name']} ({away['record']}) @ {home['name']} ({home['record']})
Date: {game_data['game_time_display']}
Venue: {game_data['venue']['name']} ({game_data['venue']['city']}, {game_data['venue']['state']})
Indoor: {'Yes' if game_data['venue']['indoor'] else 'No'}
Broadcast: {game_data['broadcast']}

HOME/AWAY SPLITS:
{home['name']}: {home['home_record']} at home
{away['name']}: {away['away_record']} on road

TEAM LEADERS:
{home['name']}:
"""
        
        if home['leaders'].get('passing'):
            prompt += f"  QB: {home['leaders']['passing']['player']} - {home['leaders']['passing']['stats']}\n"
        if home['leaders'].get('rushing'):
            prompt += f"  RB: {home['leaders']['rushing']['player']} - {home['leaders']['rushing']['stats']}\n"
        if home['leaders'].get('receiving'):
            prompt += f"  WR: {home['leaders']['receiving']['player']} - {home['leaders']['receiving']['stats']}\n"
        
        prompt += f"\n{away['name']}:\n"
        
        if away['leaders'].get('passing'):
            prompt += f"  QB: {away['leaders']['passing']['player']} - {away['leaders']['passing']['stats']}\n"
        if away['leaders'].get('rushing'):
            prompt += f"  RB: {away['leaders']['rushing']['player']} - {away['leaders']['rushing']['stats']}\n"
        if away['leaders'].get('receiving'):
            prompt += f"  WR: {away['leaders']['receiving']['player']} - {away['leaders']['receiving']['stats']}\n"
        
        prompt += "\nBETTING LINES:\n"
        
        if odds:
            prompt += f"""Spread: {odds.get('spread_details', 'N/A')}
Over/Under: {odds.get('over_under', 'N/A')}
Moneyline: {home['abbreviation']} {odds.get('home_moneyline', 'N/A')} / {away['abbreviation']} {odds.get('away_moneyline', 'N/A')}
Source: {odds.get('provider', 'N/A')}
"""
        else:
            prompt += "Odds not yet available\n"
        
        return prompt

if __name__ == "__main__":
    # Test with current data
    import requests
    
    url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
    response = requests.get(url)
    data = response.json()
    
    extractor = ESPNDataExtractor(data)
    games = extractor.get_all_games()
    
    print(f"Found {len(games)} games")
    
    if games:
        print("\nSample game with leaders:")
        print(json.dumps(games[0], indent=2))
        
        print("\n" + "="*60)
        print("AI PROMPT FORMAT:")
        print("="*60)
        print(extractor.prepare_for_ai(games[0]))
