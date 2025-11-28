# NFL Betting Platform - Data Pipeline

Complete backend pipeline for your NFL betting platform. Fetches ESPN data, generates AI analysis, ready to integrate with Supabase.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install openai requests
```

### 2. Set Your OpenAI API Key

```bash
export OPENAI_API_KEY="your-key-here"
```

### 3. Run the Pipeline

```bash
# Run with current week
python pipeline.py

# Run specific week
WEEK=13 python pipeline.py
```

## 📁 Project Structure

```
.
├── pipeline.py           # Main daily pipeline
├── espn_extractor.py     # Parses ESPN API data
├── ai_analyzer.py        # Generates AI insights
├── espn_test.py          # Test ESPN API access
├── mock_espn_data.json   # Sample data for testing
└── output/               # Generated analyses (JSON)
```

## 🔧 How It Works

### Step 1: Fetch ESPN Data

```python
# ESPN's free API endpoints
scoreboard = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
team_info = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams/{team_id}"
```

The pipeline fetches:
- Current week's games
- Team records
- Odds (spread, O/U, moneyline)
- Venue info
- Broadcast details

### Step 2: Extract & Structure

`ESPNDataExtractor` parses the messy ESPN JSON into clean structures:

```json
{
  "game_id": "401671890",
  "home_team": {
    "name": "Detroit Lions",
    "record": "10-1",
    ...
  },
  "odds": {
    "spread": -10.5,
    "over_under": 48.5,
    ...
  }
}
```

### Step 3: AI Analysis

`NFLAnalyzer` sends each game to OpenAI (GPT-4) and generates:

```json
{
  "top_insight": "One key sentence",
  "summary": "2-3 paragraphs of context",
  "ai_lean": "Lean: Lions -10.5",
  "angles": [
    "Detroit is 8-2 ATS at home",
    "Bears 1-5 ATS on road in division",
    ...
  ],
  "predicted_line": "DET -11",
  "predicted_total": "49",
  "team_strength": {
    "home_offense": "92",
    "home_defense": "85",
    ...
  },
  "injury_impact": "Minor",
  "confidence_score": "High"
}
```

### Step 4: Save Results

Currently saves to `output/` as JSON files.

**Ready for Supabase:** Just swap the `save_to_database()` function to use Supabase client.

## 💰 Cost Breakdown

Using GPT-4 (gpt-4o-mini recommended for cost savings):

- ~$0.10-0.20 per game analysis
- ~16 games/week during regular season
- **~$2-3/week or ~$8-12/month**

You can switch models in `ai_analyzer.py`:
```python
NFLAnalyzer(model="gpt-4o-mini")  # Cheaper
NFLAnalyzer(model="gpt-4o")       # Smarter
```

## 🗓️ Running Daily

### Option 1: Cron (Linux/Mac)

```bash
# Edit crontab
crontab -e

# Add this line (runs at 3 AM daily)
0 3 * * * cd /path/to/project && /usr/bin/python3 pipeline.py >> pipeline.log 2>&1
```

### Option 2: Vercel Cron (Next.js API route)

```typescript
// pages/api/cron/analyze-games.ts
export default async function handler(req, res) {
  // Call your Python pipeline or rewrite in TypeScript
  // Verify cron secret from Vercel
  
  if (req.query.secret !== process.env.CRON_SECRET) {
    return res.status(401).json({ message: 'Unauthorized' });
  }
  
  // Run pipeline...
  res.status(200).json({ success: true });
}
```

### Option 3: DigitalOcean Droplet (what you're used to)

1. SSH into your droplet
2. Clone this repo
3. Set up cron as shown above
4. Logs go to `pipeline.log`

## 🔄 Next Steps: Integrate with Supabase

### 1. Create Tables

```sql
-- Raw ESPN data
CREATE TABLE games_raw (
  id BIGSERIAL PRIMARY KEY,
  game_id TEXT UNIQUE NOT NULL,
  raw_json JSONB NOT NULL,
  fetched_at TIMESTAMP DEFAULT NOW()
);

-- AI Analysis
CREATE TABLE ai_outputs (
  id BIGSERIAL PRIMARY KEY,
  game_id TEXT UNIQUE NOT NULL,
  top_insight TEXT,
  summary TEXT,
  ai_lean TEXT,
  angles JSONB,  -- Array of strings
  predicted_line TEXT,
  predicted_total TEXT,
  team_strength JSONB,
  injury_impact TEXT,
  confidence_score TEXT,
  analyzed_at TIMESTAMP DEFAULT NOW(),
  
  FOREIGN KEY (game_id) REFERENCES games_raw(game_id)
);

-- Users (already exists in Supabase)
-- Subscriptions
CREATE TABLE subscriptions (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id),
  active BOOLEAN DEFAULT false,
  plan TEXT DEFAULT 'monthly',
  stripe_customer_id TEXT,
  stripe_subscription_id TEXT,
  last_payment_date TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### 2. Update pipeline.py

```python
from supabase import create_client

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

def save_to_database(self, results):
    for result in results:
        # Save raw data
        supabase.table('games_raw').upsert({
            'game_id': result['game_data']['game_id'],
            'raw_json': result['game_data']
        }).execute()
        
        # Save analysis
        supabase.table('ai_outputs').upsert({
            'game_id': result['game_data']['game_id'],
            'top_insight': result['analysis']['top_insight'],
            'summary': result['analysis']['summary'],
            'ai_lean': result['analysis']['ai_lean'],
            'angles': result['analysis']['angles'],
            'predicted_line': result['analysis']['predicted_line'],
            'predicted_total': result['analysis']['predicted_total'],
            'team_strength': result['analysis']['team_strength'],
            'injury_impact': result['analysis']['injury_impact'],
            'confidence_score': result['analysis']['confidence_score']
        }).execute()
```

## 🧪 Testing

### Test ESPN API Access

```bash
python espn_test.py
```

This will:
- Fetch current scoreboard
- Fetch Week 13 games
- Save sample JSON files
- Show you what data is available

### Test with Mock Data

```bash
# No API key needed
python pipeline.py
```

Uses `mock_espn_data.json` to simulate the full pipeline.

### Test with Real OpenAI

```bash
export OPENAI_API_KEY="sk-..."
python pipeline.py
```

Costs ~$0.20 for the 2 mock games.

## 📊 Output Format

Each batch creates:

```
output/
├── batch_20251128_143433.json      # Complete batch with stats
├── game_401671890_20251128.json    # Individual game + analysis
└── game_401671891_20251128.json
```

**Ready to query** from your Next.js frontend!

## 🎯 Frontend Integration (Next.js)

```typescript
// pages/api/games.ts
export default async function handler(req, res) {
  const { data } = await supabase
    .from('ai_outputs')
    .select(`
      *,
      games_raw!inner(raw_json)
    `)
    .order('analyzed_at', { ascending: false });
  
  res.json(data);
}

// pages/index.tsx
const { data: games } = await fetch('/api/games').then(r => r.json());

{games.map(game => (
  <GameCard
    insight={game.top_insight}
    lean={game.ai_lean}
    spread={game.raw_json.odds.spread_details}
  />
))}
```

## ⚡ Performance Tips

1. **Cache ESPN responses** (5-10 min): Reduces API calls
2. **Batch AI requests**: Send multiple games in one request (custom prompt)
3. **Use gpt-4o-mini**: 10x cheaper, still great for this use case
4. **Only re-analyze on changes**: Check if odds/injuries changed

## 🚨 Important Notes

### ESPN API Terms of Service

- ESPN's API is technically not public
- No official rate limits documented
- Used by many fantasy/betting apps
- Consider SportsData.io ($30/mo) for production if needed

### AI Prompt Engineering

The system prompt in `ai_analyzer.py` is critical:
- **Never guarantees** - "lean", "favor", "suggest"
- **Factual tone** - no hype
- **Compliance-ready** - avoids "lock", "sure thing"

Tweak it based on your voice/brand.

### Error Handling

Pipeline is fault-tolerant:
- Continues if one game fails
- Saves error status
- Logs all issues to stats

## 📝 TODO / Roadmap

- [ ] Add team statistics API calls
- [ ] Fetch injury reports
- [ ] Integrate odds API (The Odds API, SportsData.io)
- [ ] Weather data for outdoor games
- [ ] Historical ATS trends from database
- [ ] Player props analysis
- [ ] Email notifications on completion
- [ ] Slack alerts on errors

## 🆘 Troubleshooting

**"ModuleNotFoundError: No module named 'openai'"**
```bash
pip install openai
```

**"The api_key client option must be set"**
```bash
export OPENAI_API_KEY="your-key"
```

**"Connection refused" when fetching ESPN**
- ESPN blocks some cloud IPs
- Test locally first
- Consider using a proxy if needed

**High OpenAI costs**
- Switch to `gpt-4o-mini` in ai_analyzer.py
- Reduce `max_tokens` in the API call
- Cache analyses longer

## 💡 Ask Finn Similarities

This pipeline is basically the same structure as Ask Finn:

| Ask Finn | NFL Platform |
|----------|--------------|
| User question | ESPN game data |
| GPT-4 response | AI analysis |
| Supabase + credits | Supabase + subscriptions |
| Chat history | Game history |
| Stripe payments | Stripe payments |

**You can reuse:**
- ✅ Supabase auth setup
- ✅ Stripe integration code
- ✅ Protected route patterns
- ✅ Subscription gating logic
- ✅ Google OAuth
- ✅ Database schema patterns

## 📧 Questions?

This is v1 of the pipeline. We can add:
- Real-time odds tracking
- Injury scraping
- Advanced statistics
- Multiple AI models
- Confidence thresholds
- Auto-posting to social

Let me know what you want to build next!
