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
        
        self.system_prompt = """You are an expert NFL betting analyst who understands point spread betting.

CRITICAL CONCEPTS - SPREAD BETTING EDUCATION:

1. THE SPREAD IS NOT ABOUT WHO WINS THE GAME
   - A favorite at -7 must win by 8+ points for the bet to WIN
   - An underdog at +7 can LOSE by up to 6 points and the bet still WINS
   - Example: Eagles -7 vs Bears +7
     * If Eagles win 24-20 (4 point margin), Bears +7 bettors WIN
     * Eagles must win 28-20 (8+ points) for Eagles -7 bettors to WIN

2. HOME FIELD ADVANTAGE
   - Typical NFL home field advantage is 2-3 points
   - Indoor vs outdoor, weather, crowd noise all factor in

3. FAVORITES VS UNDERDOGS
   - NFL favorites cover the spread only ~49% of the time
   - Underdogs of 7+ points cover ~52% of the time historically
   - Public heavily bets favorites, creating value on underdogs
   - You should be picking underdogs in 40-50% of games if you're calibrated

4. LINE VALUE
   - If you think Eagles should be -4, but line is -7, there's VALUE on Bears +7
   - If you think a game totals 44 points, but line is 48, there's VALUE on Under
   - The question isn't "who's better?" but "who's undervalued by the line?"

Your analysis should be:
- Data-driven and factual
- Focused on finding value, not just picking better teams
- Honest about uncertainty
- Willing to back underdogs when warranted

NEVER use: "lock", "guaranteed", "sure thing", "can't lose"
ALWAYS be measured: "lean", "favor", "value", "suggests"
"""

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
        
        prompt = f"""Analyze this NFL Week {game_data['week']} matchup and find the betting value.

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
        
        prompt += "\n\nYOUR TASK:\n"
        prompt += "1. First, predict what YOU think the spread should be based on the matchup\n"
        prompt += "2. Then compare your prediction to the current Vegas line (shown below)\n"
        prompt += "3. Identify where the betting value exists\n"
        
        if odds and odds.get('spread'):
            prompt += f"\nCURRENT VEGAS LINE: {odds.get('spread_details', 'N/A')}\n"
            prompt += f"Over/Under: {odds.get('over_under', 'N/A')}\n"
        else:
            prompt += "\nVegas lines not yet available - make your own prediction\n"
        
        prompt += """

RESPOND IN THIS EXACT FORMAT:

TOP_INSIGHT:
[One compelling sentence about the key betting angle in this game]

SUMMARY:
[2-3 paragraphs analyzing both teams, recent form, key matchups, and situational factors]

YOUR_PREDICTED_SPREAD:
[What you think the spread should be, format: "TEAM -X.X" or "TEAM +X.X"]
[Explanation: Why this number? What factors led you here?]

PREDICTED_TOTAL:
[Your predicted total points, e.g., "47.5"]

VALUE_ANALYSIS:
[Compare your prediction to Vegas line if available. Where's the value?]
[If your line differs from Vegas by 2+ points, that's significant value]

AI_LEAN:
[Your betting recommendation in format "TEAM +/-X.X" or "Over/Under X.X"]
[This should be whichever side offers VALUE based on your analysis]
[Remember: Underdogs can LOSE the game and still cover. Don't just pick who you think wins.]

ANGLES:
[3-5 bullet points of specific betting angles, trends, or factors]
- [Include specific stats, situational spots, trends]
- [Look for underdog value if line seems inflated]
- [Consider home/away trends, divisional factors]
- [Note any pace of play or defensive factors for total]

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
        
        # Use YOUR_PREDICTED_SPREAD or fall back to PREDICTED_LINE
        predicted_line = sections.get('your_predicted_spread') or sections.get('predicted_line', 'TBD')
        # Clean up - take just the first line if there's an explanation
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
