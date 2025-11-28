#!/usr/bin/env python3
"""
NFL Betting Platform - Daily Pipeline
Fetches ESPN data, generates AI analysis, stores in database

Run this daily at 3 AM via cron or similar
"""

import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List
import requests

# Import our modules
from espn_extractor import ESPNDataExtractor
from ai_analyzer import NFLAnalyzer

class NFLDataPipeline:
    """Complete data pipeline for NFL betting platform"""
    
    def __init__(self, 
                 season_year: int = 2025,
                 use_mock_data: bool = False,
                 openai_api_key: str = None):
        
        self.season_year = season_year
        self.use_mock_data = use_mock_data
        
        # Set up AI analyzer
        if openai_api_key:
            os.environ['OPENAI_API_KEY'] = openai_api_key
        
        self.analyzer = NFLAnalyzer()
        
        # Stats
        self.stats = {
            'games_fetched': 0,
            'games_analyzed': 0,
            'errors': []
        }
    
    def fetch_espn_data(self, week: int = None) -> Dict:
        """
        Fetch current week's games from ESPN
        
        Args:
            week: Specific week number, or None for current week
        """
        
        if self.use_mock_data:
            print("📦 Using mock data...")
            with open('mock_espn_data.json', 'r') as f:
                return json.load(f)
        
        try:
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
    
    def process_games(self, raw_data: Dict) -> List[Dict]:
        """
        Extract and analyze all games
        
        Returns:
            List of complete game + analysis objects
        """
        
        if not raw_data:
            return []
        
        # Extract game data
        extractor = ESPNDataExtractor(raw_data)
        games = extractor.get_all_games()
        
        print(f"\n📊 Processing {len(games)} games...")
        
        results = []
        
        for i, game in enumerate(games, 1):
            print(f"\n{'='*60}")
            print(f"Game {i}/{len(games)}: {game['away_team']['name']} @ {game['home_team']['name']}")
            print(f"{'='*60}")
            
            try:
                # Generate AI analysis
                print("🤖 Generating AI analysis...")
                analysis = self.analyzer.analyze_game(game)
                
                # Combine game data + analysis
                complete_record = {
                    'game_data': game,
                    'analysis': analysis,
                    'processed_at': datetime.utcnow().isoformat(),
                    'status': 'complete'
                }
                
                results.append(complete_record)
                self.stats['games_analyzed'] += 1
                
                print("✅ Analysis complete")
                
            except Exception as e:
                error_msg = f"Failed to analyze game {game['game_id']}: {e}"
                print(f"❌ {error_msg}")
                self.stats['errors'].append(error_msg)
                
                # Still save with error status
                complete_record = {
                    'game_data': game,
                    'analysis': None,
                    'processed_at': datetime.utcnow().isoformat(),
                    'status': 'error',
                    'error': str(e)
                }
                results.append(complete_record)
        
        return results
    
    def save_to_database(self, results: List[Dict]):
        """
        Save results to database
        
        In production, this would write to Supabase
        For now, we'll save to JSON files
        """
        
        print(f"\n{'='*60}")
        print("💾 SAVING RESULTS")
        print(f"{'='*60}")
        
        # Create output directory
        os.makedirs('output', exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save complete batch
        batch_file = f"output/batch_{timestamp}.json"
        with open(batch_file, 'w') as f:
            json.dump({
                'timestamp': timestamp,
                'stats': self.stats,
                'games': results
            }, f, indent=2)
        
        print(f"✅ Saved batch: {batch_file}")
        
        # Save individual game files
        for result in results:
            game_id = result['game_data']['game_id']
            game_file = f"output/game_{game_id}_{timestamp}.json"
            
            with open(game_file, 'w') as f:
                json.dump(result, f, indent=2)
            
            print(f"  • Saved: game_{game_id}_{timestamp}.json")
        
        return batch_file
    
    def run(self, week: int = None):
        """
        Run the complete pipeline
        
        Args:
            week: Specific week to process, or None for current
        """
        
        print("="*60)
        print("🏈 NFL BETTING PLATFORM - DAILY PIPELINE")
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
        
        # Step 2: Process games
        print("\n🔧 STEP 2: Processing Games")
        results = self.process_games(raw_data)
        
        # Step 3: Save to database
        print("\n💾 STEP 3: Saving to Database")
        batch_file = self.save_to_database(results)
        
        # Final stats
        print("\n" + "="*60)
        print("✅ PIPELINE COMPLETE")
        print("="*60)
        print(f"Games fetched: {self.stats['games_fetched']}")
        print(f"Games analyzed: {self.stats['games_analyzed']}")
        print(f"Errors: {len(self.stats['errors'])}")
        
        if self.stats['errors']:
            print("\nErrors encountered:")
            for error in self.stats['errors']:
                print(f"  • {error}")
        
        print(f"\nBatch saved to: {batch_file}")
        print("="*60)

def main():
    """Main entry point"""
    
    # Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    SEASON_YEAR = int(os.getenv('SEASON_YEAR', '2025'))
    WEEK = os.getenv('WEEK')  # Optional: specific week
    
    # For testing, use mock data if no API key
    USE_MOCK = not OPENAI_API_KEY
    
    if USE_MOCK:
        print("⚠️  No OPENAI_API_KEY found - using mock data for testing")
        print("Set with: export OPENAI_API_KEY='your-key-here'\n")
    
    # Run pipeline
    pipeline = NFLDataPipeline(
        season_year=SEASON_YEAR,
        use_mock_data=USE_MOCK,
        openai_api_key=OPENAI_API_KEY
    )
    
    pipeline.run(week=int(WEEK) if WEEK else None)

if __name__ == "__main__":
    main()
