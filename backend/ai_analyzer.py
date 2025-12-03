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
        
        if not os.getenv('OPENAI_API_KEY'):
            raise ValueError("OPENAI_API_KEY not found in environment")
        
        self.system_prompt = """You are an expert NFL betting analyst specializing in point spread analysis.

KEY CONCEPTS:

UNDERSTANDING THE SPREAD:
- The spread represents the expected margin of victory
- "Patriots -9" means Patriots must win by 10+ points for that bet to win
- "Giants +9" means Giants can lose by 8 or less (or win outright) for that bet to win
- Your job: Determine if the favorite will exceed the spread or fall short of it

REFRAME EVERY GAME:
Instead of "Who will win?", ask:
- "Will the favorite win by MORE than the spread?" = Bet the favorite
- "Will the margin be LESS than the spread?" = Bet the underdog

EXAMPLE:
Eagles -7 vs Bears +7
- Don't ask: "Will Eagles win?" (probably yes)
- Ask: "Will Eagles win by 8+ points?" (much less certain)
- If you think Eagles win 24-20 (4 pts), the answer is NO → Bet Bears +7

CALIBRATION:
- In a typical week, underdogs cover 40-50% of spreads
- If you're picking favorites in 90%+ of games, you're miscalibrated
- Look for spots where the favorite wins but doesn't cover

Be measured, factual, and focus on margin of victory relative to the line."""

    def analyze_game(self, game_data: Dict) -> Dict:
        """Generate complete analysis for a single game"""
        
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
        
        # Determine who's favored and by how much
        spread_info = ""
        if odds and odds.get('spread_details'):
            spread = odds.get('spread_details')
            spread_info = f"\nCURRENT SPREAD: {spread}"
        
        prompt = f"""NFL BETTING ANALYSIS - Week {game_data['week']}

MATCHUP:
{away['name']} ({away['record']}) @ {home['name']} ({home['record']})
Venue: {game_data['venue']['name']} ({'Indoor' if game_data['venue']['indoor'] else 'Outdoor'})
{game_data['venue']['city']}, {game_data['venue']['state']}

RECORDS:
{home['name']}: {home['home_record']} at home
{away['name']}: {away['away_record']} on road
"""

        # Add team leaders
        if 'leaders' in home and home['leaders']:
            prompt += f"""
KEY PLAYERS:
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
        
        prompt += spread_info
        
        if odds and odds.get('over_under'):
            prompt += f"\nTotal: {odds.get('over_under')}"
        
        # THE KEY QUESTION
        if odds and odds.get('spread_details'):
            spread = odds.get('spread_details')
            prompt += f"""

THE CRITICAL QUESTION:
Given the spread of {spread}, answer this:

Will the favorite cover this spread (win by more than the number), 
OR will the underdog cover (lose by less than the number or win outright)?

Think about:
1. What's the most likely score/margin?
2. Is that margin bigger or smaller than the spread?
3. What factors could keep the game closer than expected?
4. What factors could lead to a blowout?

Don't just pick who wins - pick who covers the SPREAD.
"""
        else:
            prompt += """

Since no spread is posted yet, predict what the spread should be and explain your reasoning.
"""
        
        prompt += """

RESPOND IN THIS FORMAT:

SUMMARY:
[2-3 paragraphs on both teams, form, matchup factors]

SPREAD_ANALYSIS:
[Answer the critical question: Will the favorite cover or will the underdog cover?]
[Explain your expected margin of victory and how it compares to the spread]

AI_LEAN:
[Your pick: Either the favorite with the spread, or the underdog with the spread]
[Format: "Patriots -9" or "Giants +9" or "Under 45.5"]

TOP_INSIGHT:
[One sentence explaining WHY your AI_LEAN pick makes sense - support your recommendation]
[If you picked the underdog, explain their path to covering]
[If you picked the favorite, explain why they'll exceed the spread]

PREDICTED_LINE:
[Format: "TEAM +/-X.X" - Your prediction of what the spread should be]

PREDICTED_TOTAL:
[Just the number, e.g., "45.5"]

ANGLES:
- [Specific betting angle 1]
- [Specific betting angle 2]
- [Specific betting angle 3]
- [Specific betting angle 4]
- [Specific betting angle 5]

TEAM_STRENGTH:
Home Offense: [0-100]
Home Defense: [0-100]
Away Offense: [0-100]
Away Defense: [0-100]

INJURY_IMPACT:
[Minor/Moderate/Significant and why]

CONFIDENCE:
[Low/Medium/High]
"""
        
        return prompt
    
    def _parse_analysis(self, text: str, game_data: Dict) -> Dict:
        """Parse the AI response into structured format"""
        
        sections = {}
        current_section = None
        current_content = []
        
        for line in text.split('\n'):
            line = line.strip()
            
            if line.endswith(':') and line.replace('_', ' ').replace(':', '').isupper():
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                
                current_section = line[:-1].lower()
                current_content = []
            elif line:
                current_content.append(line)
        
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()
        
        # Extract angles
        angles = []
        if 'angles' in sections:
            angles = [
                line.strip('- ').strip() 
                for line in sections['angles'].split('\n') 
                if line.strip() and line.strip().startswith('-')
            ]
        
        # Parse team strength
        team_strength = {}
        if 'team_strength' in sections:
            for line in sections['team_strength'].split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower().replace(' ', '_')
                    value = value.strip().split()[0]
                    team_strength[key] = value
        
        predicted_line = sections.get('predicted_line', 'TBD')
        if '\n' in predicted_line:
            predicted_line = predicted_line.split('\n')[0].strip()
        
        return {
            'top_insight': sections.get('top_insight', 'Analysis unavailable'),
            'summary': sections.get('summary', 'No summary available'),
            'ai_lean': sections.get('ai_lean', 'No recommendation'),
            'angles': angles,
            'predicted_line': predicted_line,
            'predicted_total': sections.get('predicted_total', 'TBD'),
            'team_strength': team_strength,
            'injury_impact': sections.get('injury_impact', 'Unknown'),
            'confidence_score': sections.get('confidence', 'Medium')
        }
    
    def _get_fallback_analysis(self, game_data: Dict) -> Dict:
        """Return basic analysis if AI fails"""
        
        home = game_data['home_team']['name']
        away = game_data['away_team']['name']
        
        return {
            'top_insight': f"{away} @ {home} - Analysis unavailable",
            'summary': f"Matchup between {away} and {home}.",
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
