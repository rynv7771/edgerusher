#!/usr/bin/env python3
"""
NFL Betting Platform - Pipeline with Supabase Integration
Fetches ESPN data, generates AI analysis, saves to Supabase
"""

import json
import os
from datetime import datetime, timezone
from typing import Dict, List
import requests
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables (works locally, GitHub Actions passes them directly)
load_dotenv()

# Import our modules
from espn_extractor import ESPNDataExtractor
from ai_analyzer import NFLAnalyzer

class NFLDataPipeline:
    """Complete data pipeline with Supabase integration"""
    
    def __init__(self, 
                 season_year: int = 2025,
                 use_mock_data: bool = False):
        
        self.season_year = season_year
        self.use_mock_data = use_mock_data
        
        # Set up Supabase - check multiple env var names
        supabase_url = os.getenv('NEXT_PUBLIC_SUPABASE_URL') or os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY')
        
        if not supabase_url or not supabase_key:
            raise ValueError(f"Missing Supabase credentials. URL: {bool(supabase_url)}, Key: {bool(supabase_key)}")
        
        print(f"✓ Supabase URL: {supabase_url}")
        print(f"✓ Supabase Key: {'*' * 20}...{supabase_key[-4:]}")
        
        self.supabase: Client = create_client(supabase_url, supabase_key)
        
        # Set up AI analyzer
        openai_key = os.getenv('OPENAI_API_KEY')
        if not openai_key:
            raise ValueError("Missing OPENAI_API_KEY")
        
        print(f"✓ OpenAI Key: {'*' * 20}...{openai_key[-4:]}")
        
        os.environ['OPENAI_API_KEY'] = openai_key
        self.analyzer = NFLAnalyzer()
        
        # Stats
        self.stats = {
            'games_fetched': 0,
            'games_analyzed': 0,
            'games_saved': 0,
            'errors': []
        }
    
    def fetch_espn_data(self, week: int = None) -> Dict:
        """Fetch upcoming week's games from ESPN"""
        
        if self.use_mock_data:
            print("📦 Using mock data...")
            with open('mock_espn_data.json', 'r') as f:
                return json.load(f)
        
        try:
            if not week:
                # Auto-detect: find the week with upcoming games
                # Try current week from ESPN, then check if games are upcoming
                base_url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
                response = requests.get(base_url, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                current_week = data.get('week', {}).get('number', 13)
                
                # Check if any games are in the future
                events = data.get('events', [])
                now = datetime.now(timezone.utc)
                
                has_upcoming = False
                for event in events:
                    game_date_str = event.get('date')
                    if game_date_str:
                        game_date = datetime.fromisoformat(game_date_str.replace('Z', '+00:00'))
                        if game_date > now:
                            has_upcoming = True
                            break
                
                if not has_upcoming:
                    # No upcoming games in current week, move to next
                    week = current_week + 1
                    print(f"📅 Week {current_week} has no upcoming games, fetching Week {week}")
                else:
                    week = current_week
                    print(f"📅 Week {week} has upcoming games")
            
            if week:
                url = f"https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?dates={self.season_year}&seasontype=2&week={week}"
            else:
                url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
            
            print(f"🏈 Fetching from ESPN: {url}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            self.stats['games_fetched'] = len(data.get('events', []))
            
            return data
            
        except Exception as e:
            error_msg = f"Failed to fetch ESPN data: {e}"
            print(f"❌ {error_msg}")
            self.stats['errors'].append(error_msg)
            return None
    
    def save_to_supabase(self, game_data: Dict, analysis: Dict) -> bool:
        """Save game and analysis to Supabase"""
        
        try:
            game_id = game_data['game_id']
            
            # 1. Save raw game data
            game_record = {
                'game_id': game_id,
                'raw_json': game_data,
                'week': game_data['week'],
                'season_year': game_data['season_year'],
                'game_time': game_data['game_time'],
                'fetched_at': datetime.now(timezone.utc).isoformat()
            }
            
            # Upsert (insert or update if exists)
            self.supabase.table('games_raw').upsert(game_record, on_conflict='game_id').execute()
            print(f"  ✅ Saved raw game data")
            
            # 2. Save AI analysis
            ai_record = {
                'game_id': game_id,
                'top_insight': analysis['top_insight'],
                'summary': analysis['summary'],
                'ai_lean': analysis['ai_lean'],
                'angles': analysis['angles'],
                'predicted_line': analysis['predicted_line'],
                'predicted_total': analysis['predicted_total'],
                'team_strength': analysis['team_strength'],
                'injury_impact': analysis['injury_impact'],
                'confidence_score': analysis['confidence_score'],
                'analyzed_at': datetime.now(timezone.utc).isoformat()
            }
            
            # Upsert AI analysis
            self.supabase.table('ai_outputs').upsert(ai_record, on_conflict='game_id').execute()
            print(f"  ✅ Saved AI analysis")
            
            self.stats['games_saved'] += 1
            return True
            
        except Exception as e:
            error_msg = f"Failed to save game {game_id}: {e}"
            print(f"  ❌ {error_msg}")
            self.stats['errors'].append(error_msg)
            return False
    
    def process_games(self, raw_data: Dict) -> int:
        """Extract and analyze all games, save to Supabase"""
        
        if not raw_data:
            return 0
        
        # Extract game data
        extractor = ESPNDataExtractor(raw_data)
        games = extractor.get_all_games()
        
        print(f"\n📊 Processing {len(games)} games...")
        
        for i, game in enumerate(games, 1):
            print(f"\n{'='*60}")
            print(f"Game {i}/{len(games)}: {game['away_team']['name']} @ {game['home_team']['name']}")
            print(f"{'='*60}")
            
            try:
                # Generate AI analysis
                print("🤖 Generating AI analysis...")
                analysis = self.analyzer.analyze_game(game)
                
                self.stats['games_analyzed'] += 1
                print("✅ Analysis complete")
                
                # Save to Supabase
                print("💾 Saving to database...")
                self.save_to_supabase(game, analysis)
                
            except Exception as e:
                error_msg = f"Failed to process game {game['game_id']}: {e}"
                print(f"❌ {error_msg}")
                self.stats['errors'].append(error_msg)
        
        return self.stats['games_saved']
    
    def run(self, week: int = None):
        """Run the complete pipeline"""
        
        print("="*60)
        print("🏈 NFL BETTING PLATFORM - PIPELINE")
        print("="*60)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Season: {self.season_year}")
        print(f"Week: {week if week else 'Current'}")
        print(f"Mock Data: {self.use_mock_data}")
        print("="*60)
        
        # Step 1: Fetch data
        print("\n📡 STEP 1: Fetching ESPN Data")
        raw_data = self.fetch_espn_data(week)
        
        if not raw_data:
            print("❌ Pipeline failed: No data fetched")
            return
        
        # Step 2: Process and save games
        print("\n🔧 STEP 2: Processing & Saving Games")
        saved_count = self.process_games(raw_data)
        
        # Final stats
        print("\n" + "="*60)
        print("✅ PIPELINE COMPLETE")
        print("="*60)
        print(f"Games fetched: {self.stats['games_fetched']}")
        print(f"Games analyzed: {self.stats['games_analyzed']}")
        print(f"Games saved to Supabase: {self.stats['games_saved']}")
        print(f"Errors: {len(self.stats['errors'])}")
        
        if self.stats['errors']:
            print("\nErrors encountered:")
            for error in self.stats['errors']:
                print(f"  • {error}")
        
        print("="*60)

def main():
    """Main entry point"""
    
    # Configuration from environment
    SEASON_YEAR = int(os.getenv('SEASON_YEAR', '2025'))
    WEEK = os.getenv('WEEK')
    USE_MOCK = os.getenv('USE_MOCK_DATA', 'false').lower() == 'true'
    
    # Run pipeline
    pipeline = NFLDataPipeline(
        season_year=SEASON_YEAR,
        use_mock_data=USE_MOCK
    )
    
    pipeline.run(week=int(WEEK) if WEEK else None)

if __name__ == "__main__":
    main()
