#!/usr/bin/env python3
"""
AI Analysis Pipeline
Generates betting insights using OpenAI API
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import openai

# You'll set this as an environment variable
# export OPENAI_API_KEY="your-key-here"
openai.api_key = os.getenv("OPENAI_API_KEY")

class NFLAnalyzer:
    """Generate AI betting insights for NFL games"""
    
    def __init__(self, model="gpt-4o-mini"):  # Using mini for cost savings, can upgrade to gpt-4o
        self.model = model
        self.system_prompt = """You are an expert NFL analyst focused on providing factual, data-driven betting insights. 

Your analysis should be:
- Clear and concise
- Based on factual information
- Free from hype or guarantees
- Honest about uncertainty
- Focused on useful angles and context

NEVER use words like: "lock", "guaranteed", "sure thing", "can't lose", "best bet ever"
ALWAYS be measured: "lean", "favor", "suggest", "indicates", "trend shows"

You analyze matchups considering:
- Team records and recent performance
- Home/away splits
- Division matchups
- Coaching tendencies
- Weather (for outdoor games)
- Rest days and schedule spots
- Historical trends (ATS, totals)
- Key injuries when provided"""

    def analyze_game(self, game_data: Dict) -> Dict:
        """
        Generate complete analysis for a single game
        Returns all AI outputs in structured format
        """
        
        prompt = self._build_analysis_prompt(game_data)
        
        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            analysis_text = response.choices[0].message.content
            
            # Parse the structured response
            analysis = self._parse_analysis(analysis_text, game_data)
            
            return analysis
            
        except Exception as e:
            print(f"Error generating analysis: {e}")
            return self._get_fallback_analysis(game_data)
    
    def _build_analysis_prompt(self, game_data: Dict) -> str:
        """Build the prompt for AI analysis"""
        
        home = game_data['home_team']
        away = game_data['away_team']
        odds = game_data.get('odds', {})
        
        prompt = f"""Analyze this NFL Week {game_data['week']} matchup and provide a complete betting breakdown.

MATCHUP:
{away['name']} ({away['record']}) @ {home['name']} ({home['record']})
Date: {game_data['game_time_display']}
Venue: {game_data['venue']['name']} ({'Indoor' if game_data['venue']['indoor'] else 'Outdoor'})
Location: {game_data['venue']['city']}, {game_data['venue']['state']}

CURRENT BETTING LINES:
"""
        
        if odds:
            prompt += f"""Spread: {odds.get('spread_details', 'N/A')}
Over/Under: {odds.get('over_under', 'N/A')}
Moneyline: {home['abbreviation']} {odds.get('home_moneyline', 'N/A')} / {away['abbreviation']} {odds.get('away_moneyline', 'N/A')}
"""
        else:
            prompt += "Lines not yet posted\n"
        
        prompt += f"""

Please provide your analysis in this exact format:

TOP_INSIGHT:
[One compelling sentence - the most important thing to know about this game]

SUMMARY:
[2-3 paragraphs providing context on both teams, recent form, key matchup factors, and why this game matters]

AI_LEAN:
[Brief statement like "Lean: [Team] [Spread/Total]" - be measured, never guarantee]

ANGLES:
[3-5 bullet points of interesting betting angles, trends, or situational spots. Include specific stats when possible]
- Angle 1
- Angle 2
- Angle 3
- Angle 4
- Angle 5

TEAM_STRENGTH:
Home Offense: [0-100 rating]
Home Defense: [0-100 rating]
Away Offense: [0-100 rating]
Away Defense: [0-100 rating]

PREDICTED_LINE:
[Your predicted spread, e.g., "DET -9.5"]

PREDICTED_TOTAL:
[Your predicted total, e.g., "47.5"]

INJURY_IMPACT:
[Minor/Moderate/Significant and brief explanation]

CONFIDENCE:
[Low/Medium/High - be honest about uncertainty]
"""
        
        return prompt
    
    def _parse_analysis(self, text: str, game_data: Dict) -> Dict:
        """Parse the AI response into structured format"""
        
        sections = {}
        current_section = None
        current_content = []
        
        for line in text.split('\n'):
            line = line.strip()
            
            # Check if this is a section header
            if line.endswith(':') and line.replace('_', ' ').replace(':', '').isupper():
                # Save previous section
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                
                # Start new section
                current_section = line[:-1].lower()
                current_content = []
            elif line:
                current_content.append(line)
        
        # Save last section
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()
        
        # Extract angles as array
        angles = []
        if 'angles' in sections:
            angles = [
                line.strip('- ').strip() 
                for line in sections['angles'].split('\n') 
                if line.strip().startswith('-')
            ]
        
        # Extract team strengths
        team_strength = {}
        if 'team_strength' in sections:
            for line in sections['team_strength'].split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    team_strength[key.strip().lower().replace(' ', '_')] = value.strip()
        
        # Build final structure
        analysis = {
            'game_id': game_data['game_id'],
            'analyzed_at': datetime.utcnow().isoformat(),
            
            # Core outputs
            'top_insight': sections.get('top_insight', 'Analysis pending'),
            'summary': sections.get('summary', ''),
            'ai_lean': sections.get('ai_lean', 'No lean at this time'),
            'angles': angles,
            
            # Predictions
            'predicted_line': sections.get('predicted_line', 'TBD'),
            'predicted_total': sections.get('predicted_total', 'TBD'),
            
            # Ratings
            'team_strength': team_strength,
            'injury_impact': sections.get('injury_impact', 'Unknown'),
            'confidence_score': sections.get('confidence', 'Medium'),
            
            # Metadata
            'model_used': self.model,
            'game_data': {
                'home_team': game_data['home_team']['name'],
                'away_team': game_data['away_team']['name'],
                'game_time': game_data['game_time_display']
            }
        }
        
        return analysis
    
    def _get_fallback_analysis(self, game_data: Dict) -> Dict:
        """Return a safe fallback if AI fails"""
        return {
            'game_id': game_data['game_id'],
            'analyzed_at': datetime.utcnow().isoformat(),
            'top_insight': 'Analysis temporarily unavailable',
            'summary': 'We are working on generating analysis for this matchup.',
            'ai_lean': 'No analysis available',
            'angles': [],
            'predicted_line': 'TBD',
            'predicted_total': 'TBD',
            'team_strength': {},
            'injury_impact': 'Unknown',
            'confidence_score': 'N/A',
            'model_used': self.model,
            'game_data': {
                'home_team': game_data['home_team']['name'],
                'away_team': game_data['away_team']['name'],
                'game_time': game_data['game_time_display']
            }
        }

def test_analyzer():
    """Test the analyzer with extracted game data"""
    
    print("="*60)
    print("AI ANALYZER TEST")
    print("="*60)
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠️  OPENAI_API_KEY not set!")
        print("Set it with: export OPENAI_API_KEY='your-key-here'")
        print("\nRunning with mock data instead...\n")
        
        # Load sample game data
        with open('game_401671890.json', 'r') as f:
            game_data = json.load(f)
        
        # Create mock analysis
        mock_analysis = {
            'game_id': game_data['game_id'],
            'analyzed_at': datetime.utcnow().isoformat(),
            'top_insight': 'The Lions are coming off a dominant performance and facing a Bears team that has struggled on the road.',
            'summary': 'Detroit enters as heavy favorites after an impressive win streak. Chicago has lost 4 of their last 5 and struggles in divisional road games. The Lions offense has been explosive at home, averaging 31 PPG at Ford Field.',
            'ai_lean': 'Lean: Lions -10.5',
            'angles': [
                'Detroit is 8-2 ATS at home this season',
                'Bears are 1-5 ATS in divisional road games',
                'Lions average 31 PPG at Ford Field',
                'Chicago defense allows 27 PPG on the road'
            ],
            'predicted_line': 'DET -11',
            'predicted_total': '49',
            'team_strength': {
                'home_offense': '92',
                'home_defense': '85',
                'away_offense': '68',
                'away_defense': '72'
            },
            'injury_impact': 'Minor - No major injuries reported',
            'confidence_score': 'High',
            'model_used': 'mock',
            'game_data': {
                'home_team': game_data['home_team']['name'],
                'away_team': game_data['away_team']['name'],
                'game_time': game_data['game_time_display']
            }
        }
        
        # Save it
        filename = f"analysis_{game_data['game_id']}.json"
        with open(filename, 'w') as f:
            json.dump(mock_analysis, f, indent=2)
        
        print(f"✅ Created mock analysis: {filename}")
        print("\nPreview:")
        print(f"Top Insight: {mock_analysis['top_insight']}")
        print(f"AI Lean: {mock_analysis['ai_lean']}")
        print(f"Angles: {len(mock_analysis['angles'])} angles generated")
        
        return
    
    # Real API test
    print("\n🤖 Testing with OpenAI API...\n")
    
    analyzer = NFLAnalyzer()
    
    # Load a game
    with open('game_401671890.json', 'r') as f:
        game_data = json.load(f)
    
    print(f"Analyzing: {game_data['away_team']['name']} @ {game_data['home_team']['name']}")
    print("This will cost ~$0.10-0.20...\n")
    
    analysis = analyzer.analyze_game(game_data)
    
    # Save it
    filename = f"analysis_{game_data['game_id']}.json"
    with open(filename, 'w') as f:
        json.dump(analysis, f, indent=2)
    
    print(f"\n✅ Analysis complete! Saved to {filename}\n")
    
    # Show preview
    print("="*60)
    print("PREVIEW")
    print("="*60)
    print(f"\nTop Insight:\n{analysis['top_insight']}")
    print(f"\nAI Lean:\n{analysis['ai_lean']}")
    print(f"\nAngles:")
    for angle in analysis['angles']:
        print(f"  • {angle}")
    print(f"\nConfidence: {analysis['confidence_score']}")

if __name__ == "__main__":
    test_analyzer()
