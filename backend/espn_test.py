#!/usr/bin/env python3
"""
ESPN NFL API Test Script
Tests what data is available from ESPN's free API
"""

import requests
import json
from datetime import datetime

def fetch_scoreboard(year=2025, week=None):
    """Fetch NFL scoreboard/schedule"""
    if week:
        url = f"https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?dates={year}&seasontype=2&week={week}"
    else:
        url = f"https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
    
    print(f"\n🏈 Fetching scoreboard...")
    print(f"URL: {url}\n")
    
    response = requests.get(url)
    data = response.json()
    
    return data

def fetch_team_info(team_id):
    """Fetch detailed team information"""
    url = f"https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams/{team_id}"
    
    print(f"\n📊 Fetching team {team_id} info...")
    
    response = requests.get(url)
    data = response.json()
    
    return data

def fetch_team_stats(team_id):
    """Fetch team statistics"""
    url = f"https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams/{team_id}/statistics"
    
    print(f"\n📈 Fetching team {team_id} stats...")
    
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Stats endpoint returned {response.status_code}")
        return None

def analyze_scoreboard_structure(data):
    """Analyze what's in the scoreboard response"""
    print("\n" + "="*60)
    print("SCOREBOARD STRUCTURE ANALYSIS")
    print("="*60)
    
    if 'events' in data:
        print(f"\n✅ Found {len(data['events'])} games")
        
        if len(data['events']) > 0:
            game = data['events'][0]
            
            print("\n📋 First game structure:")
            print(f"  - Game ID: {game.get('id')}")
            print(f"  - Date: {game.get('date')}")
            print(f"  - Name: {game.get('name')}")
            print(f"  - Status: {game.get('status', {}).get('type', {}).get('description')}")
            
            if 'competitions' in game and len(game['competitions']) > 0:
                comp = game['competitions'][0]
                print(f"\n  Competition data available:")
                print(f"    - Venue: {comp.get('venue', {}).get('fullName', 'N/A')}")
                print(f"    - Broadcast: {comp.get('broadcasts', [{}])[0].get('names', ['N/A'])[0] if comp.get('broadcasts') else 'N/A'}")
                
                if 'competitors' in comp:
                    print(f"    - Teams: {len(comp['competitors'])} teams")
                    for team in comp['competitors']:
                        print(f"      • {team.get('team', {}).get('displayName')} (ID: {team.get('team', {}).get('id')})")
                        print(f"        Score: {team.get('score', 'N/A')}")
                        print(f"        Record: {team.get('records', [{}])[0].get('summary', 'N/A') if team.get('records') else 'N/A'}")
                
                # Check for odds
                if 'odds' in comp and len(comp.get('odds', [])) > 0:
                    odds = comp['odds'][0]
                    print(f"\n  💰 Odds data available:")
                    print(f"    - Provider: {odds.get('provider', {}).get('name')}")
                    print(f"    - Spread: {odds.get('details')}")
                    print(f"    - Over/Under: {odds.get('overUnder')}")
                else:
                    print(f"\n  ⚠️  No odds data in this game")
                
                # Check for news/headlines
                if 'headlines' in game:
                    print(f"\n  📰 Headlines: {len(game.get('headlines', []))} available")
    
    # Check season info
    if 'season' in data:
        season = data['season']
        print(f"\n📅 Season Info:")
        print(f"  - Year: {season.get('year')}")
        print(f"  - Type: {season.get('type')}")
        
    if 'week' in data:
        print(f"  - Week: {data['week'].get('number')}")

def save_sample_data(data, filename):
    """Save sample data to file"""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"\n💾 Saved sample data to {filename}")

if __name__ == "__main__":
    print("="*60)
    print("ESPN NFL API EXPLORER")
    print("="*60)
    
    # Test 1: Current scoreboard
    print("\n🔍 TEST 1: Current Scoreboard")
    scoreboard = fetch_scoreboard()
    analyze_scoreboard_structure(scoreboard)
    save_sample_data(scoreboard, "sample_scoreboard.json")
    
    # Test 2: Specific week (Week 13 of 2025 season)
    print("\n\n🔍 TEST 2: Week 13 Scoreboard")
    week_data = fetch_scoreboard(year=2025, week=13)
    save_sample_data(week_data, "sample_week13.json")
    
    # Test 3: Team info (Chiefs = 12)
    print("\n\n🔍 TEST 3: Team Information")
    team_data = fetch_team_info("12")
    save_sample_data(team_data, "sample_team.json")
    
    # Test 4: Team stats
    print("\n\n🔍 TEST 4: Team Statistics")
    stats_data = fetch_team_stats("12")
    if stats_data:
        save_sample_data(stats_data, "sample_team_stats.json")
    
    print("\n" + "="*60)
    print("✅ EXPLORATION COMPLETE")
    print("="*60)
    print("\nCheck the generated JSON files to see full data structures:")
    print("  - sample_scoreboard.json")
    print("  - sample_week13.json") 
    print("  - sample_team.json")
    print("  - sample_team_stats.json")
