#!/usr/bin/env python3
"""
AI Analyzer for NFL Games using OpenAI
"""

import os
from typing import Dict, List
import openai

class NFLAnalyzer:
    """Generates betting analysis using OpenAI"""
    
    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        
        # Ensure API key is set
        if not os.getenv('OPENAI_API_KEY'):
            raise ValueError("OPENAI_API_KEY not found in environment")
        
        self.system_prompt = """You are an expert NFL analyst focused on providing factual, data-driven betting insights. 

Your analysis should be:
- Clear and concise
- Based on factual information
- Free from hype or guarantees
- Honest about uncertainty
- Focused on useful angles and context
- Willing to recommend underdogs when they offer value

IMPORTANT: Don't just pick favorites every time. Consider underdogs when:
- Home team is underrated
- Situational spots favor the dog
- Line seems inflated
- Public is heavily on favorite

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

HOME/AWAY SPLITS:
{home['name']}: {home['home_record']} at home
{away['name']}: {away['away_record']} on road
"""

        # Add team leaders if available
        if 'leaders' in home and home['leaders']:
            prompt += f"""
TEAM LEADERS:
{home['name']}:"""
            if 'passing' in home['leaders']:
                prompt += f"\n  QB: {home['leaders']['passing']['player']} - {home['leaders']['passing']['stats']}"
            if 'rushing' in home['leaders']:
                prompt += f"\n  RB: {home['leaders']['rushing']['player']} - {home['leaders']['rushing']['stats']}"
            if 'receiving' in home['leaders']:
                prompt += f"\n  WR: {home['leaders']['receiving']['player']} - {home['leaders']['receiving']['stats']}"
            
            prompt += f"\n\n{away['name']}:"
            if 'passing' in away['leaders']:
                prompt += f"\n  QB: {away['leaders']['passing']['player']} - {away['leaders']['passing']['stats']}"
            if 'rushing' in away['leaders']:
                prompt += f"\n  RB: {away['leaders']['rushing']['player']} - {away['leaders']['rushing']['stats']}"
            if 'receiving' in away['leaders']:
                prompt += f"\n  WR: {away['leaders']['receiving']['player']} - {away['leaders']['receiving']['stats']}"
        
        prompt += "\n\nCURRENT BETTING LINES:\n"
        
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

PREDICTED_LINE:
[Your predicted spread in format "TEAM -X.X" or "TEAM +X.X", e.g., "Lions -9.5" or "Bears +7"]

PREDICTED_TOTAL:
[Your predicted total, e.g., "47.5"]

AI_LEAN:
[Your betting recommendation using your predicted line - MUST match PREDICTED_LINE format exactly]
[Examples: "Eagles -6.5", "Bears +7", "Under 45.5"]
[Be measured: Use words like "Lean" or "Favor" - never guarantee]

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
                if line.strip() and line.strip().startswith('-')
            ]
        
        # Parse team strength ratings
        team_strength = {}
        if 'team_strength' in sections:
            for line in sections['team_strength'].split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    # Convert to snake_case
                    key = key.strip().lower().replace(' ', '_')
                    # Extract numeric value
                    value = value.strip().split()[0]
                    team_strength[key] = value
        
        return {
            'top_insight': sections.get('top_insight', 'Analysis unavailable'),
            'summary': sections.get('summary', 'No summary available'),
            'ai_lean': sections.get('ai_lean', 'No recommendation'),
            'angles': angles,
            'predicted_line': sections.get('predicted_line', 'TBD'),
            'predicted_total': sections.get('predicted_total', 'TBD'),
            'team_strength': team_strength,
            'injury_impact': sections.get('injury_impact', 'Unknown'),
            'confidence_score': sections.get('confidence', 'Medium')
        }
    
    def _get_fallback_analysis(self, game_data: Dict) -> Dict:
        """Return a basic analysis if AI fails"""
        
        home = game_data['home_team']['name']
        away = game_data['away_team']['name']
        
        return {
            'top_insight': f"{away} @ {home} - Analysis temporarily unavailable",
            'summary': f"Matchup between {away} and {home}. Full analysis coming soon.",
            'ai_lean': 'No recommendation',
            'angles': ['Analysis unavailable'],
            'predicted_line': 'TBD',
            'predicted_total': 'TBD',
            'team_strength': {
                'home_offense': '50',
                'home_defense': '50',
                'away_offense': '50',
                'away_defense': '50'
            },
            'injury_impact': 'Unknown',
            'confidence_score': 'Low'
        }
