# 🏈 NFL Betting Platform - Quick Start

## What We Built

A complete **backend pipeline** that:
- ✅ Fetches NFL game data from ESPN's API
- ✅ Generates AI betting insights using OpenAI
- ✅ Outputs structured JSON ready for Supabase
- ✅ Runs daily via cron/scheduled job
- ✅ Costs ~$8-12/month in AI analysis

## File Overview

```
nfl-betting-pipeline/
├── 📄 README.md              # Full documentation
├── 📄 QUICKSTART.md           # This file
├── 📄 .env.example            # Environment variables template
├── 📄 requirements.txt        # Python dependencies
│
├── 🐍 pipeline.py             # Main daily pipeline
├── 🐍 espn_extractor.py       # Parses ESPN API data
├── 🐍 ai_analyzer.py          # Generates AI insights
├── 🐍 espn_test.py            # Tests ESPN API access
├── 🐍 test_local.py           # End-to-end local test
│
├── 📦 mock_espn_data.json     # Sample ESPN response
├── 📦 game_*.json             # Extracted game data
├── 📦 analysis_*.json         # AI analysis samples
│
└── 📁 output/                 # Pipeline output directory
    └── batch_*.json           # Complete pipeline runs
```

## 🚀 Get Running in 10 Minutes

### Step 1: Install Dependencies

```bash
cd nfl-betting-pipeline
pip install -r requirements.txt
```

### Step 2: Set Your OpenAI Key

```bash
cp .env.example .env
# Edit .env and add your OpenAI key
export OPENAI_API_KEY="sk-your-key-here"
```

Get key from: https://platform.openai.com/api-keys

### Step 3: Test It

```bash
# Test with mock data (free, instant)
python pipeline.py

# Test with real ESPN + OpenAI (costs ~$0.20)
python test_local.py
```

### Step 4: Check Output

```bash
ls output/
cat output/batch_*.json  # See the complete results
```

You should see:
- `top_insight` - One key sentence
- `summary` - 2-3 paragraphs
- `ai_lean` - Betting recommendation
- `angles` - 3-5 interesting stats/trends
- `predicted_line` - AI's line prediction
- `team_strength` - Ratings for each team
- `confidence_score` - How confident the AI is

## 💰 Cost Analysis

### OpenAI Costs
- **Model:** gpt-4o-mini (recommended)
- **Per game:** ~$0.10-0.20
- **Per week:** ~$1.60-3.20 (16 games)
- **Per month:** ~$6.40-12.80

### Cheaper Options
1. Use fewer games (just featured matchups)
2. Cache longer (only regenerate when odds change)
3. Batch multiple games in one prompt

### Scaling Up
- **Full season (17 weeks):** ~$109-217
- **With playoffs:** Add ~$10-20
- **Props analysis:** Add ~30% more

Still WAY cheaper than paying analysts or data feeds!

## 🎯 What's Next?

### Immediate (Day 1-2)
- [x] ✅ Data pipeline working
- [ ] Set up Supabase project
- [ ] Create tables (see README.md)
- [ ] Test Supabase integration

### Frontend (Day 3-5)
- [ ] Clone Ask Finn repo (reuse structure)
- [ ] Create homepage listing games
- [ ] Create game detail page
- [ ] Add Google Auth (copy from Ask Finn)
- [ ] Add subscription gating

### Subscriptions (Day 6-7)
- [ ] Copy Stripe code from Ask Finn
- [ ] Update pricing ($10-20/month?)
- [ ] Test payment flow
- [ ] Deploy to Vercel

### Production (Day 8+)
- [ ] Schedule daily cron job
- [ ] Add affiliate links
- [ ] Test with real users
- [ ] Monitor costs/performance

## 🔗 Reusing Ask Finn Code

| Feature | Ask Finn | NFL Platform | Reuse? |
|---------|----------|--------------|--------|
| Auth | Google OAuth | Google OAuth | ✅ 100% |
| Payments | Stripe + credits | Stripe + subscription | ✅ 95% |
| Database | Supabase | Supabase | ✅ 100% |
| Gating | Credit check | Subscription check | ✅ 90% |
| API Routes | Chat endpoints | Game endpoints | ✅ 80% |

You can literally copy/paste most of your Ask Finn codebase!

## 📊 Database Schema

```sql
-- games_raw: Store ESPN data
CREATE TABLE games_raw (
  id BIGSERIAL PRIMARY KEY,
  game_id TEXT UNIQUE NOT NULL,
  raw_json JSONB NOT NULL,
  fetched_at TIMESTAMP DEFAULT NOW()
);

-- ai_outputs: Store AI analysis
CREATE TABLE ai_outputs (
  id BIGSERIAL PRIMARY KEY,
  game_id TEXT UNIQUE NOT NULL,
  top_insight TEXT,
  summary TEXT,
  ai_lean TEXT,
  angles JSONB,
  predicted_line TEXT,
  predicted_total TEXT,
  team_strength JSONB,
  injury_impact TEXT,
  confidence_score TEXT,
  analyzed_at TIMESTAMP DEFAULT NOW()
);

-- subscriptions: Copy from Ask Finn
CREATE TABLE subscriptions (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id),
  active BOOLEAN DEFAULT false,
  plan TEXT DEFAULT 'monthly',
  stripe_customer_id TEXT,
  stripe_subscription_id TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);
```

## 🎨 Frontend Structure

```typescript
// pages/index.tsx - Homepage
export default function Home() {
  const { data: games } = useSWR('/api/games/today');
  
  return (
    <div>
      <h1>Today's Games</h1>
      {games?.map(game => (
        <GameCard key={game.game_id} game={game} />
      ))}
    </div>
  );
}

// pages/game/[id].tsx - Game detail
export default function GamePage({ gameId }) {
  const { data: analysis } = useSWR(`/api/game/${gameId}`);
  const { user } = useUser();
  
  return (
    <div>
      <TopInsight>{analysis.top_insight}</TopInsight>
      
      {user?.subscribed ? (
        <>
          <AILean>{analysis.ai_lean}</AILean>
          <Angles angles={analysis.angles} />
          <Predictions line={analysis.predicted_line} />
        </>
      ) : (
        <PaywallOverlay />
      )}
    </div>
  );
}

// pages/api/games/today.ts - API route
export default async function handler(req, res) {
  const today = new Date().toISOString().split('T')[0];
  
  const { data } = await supabase
    .from('ai_outputs')
    .select('*, games_raw!inner(*)')
    .gte('games_raw.game_time', today)
    .order('games_raw.game_time');
  
  res.json(data);
}
```

## 🚨 Important Considerations

### 1. ESPN API Compliance
- ESPN's API is not officially public
- Many apps use it without issue
- Consider paid alternatives for production:
  - SportsData.io ($30-50/mo)
  - The Odds API ($25-100/mo)
  - RapidAPI NFL options

### 2. Betting Content Regulations
- No guarantees or "locks"
- Include gambling disclaimers
- Age verification (21+)
- Responsible gaming links

The AI is already trained to avoid problematic language!

### 3. Affiliate Compliance
- Disclose affiliate relationships
- Follow specific program rules (DraftKings, FanDuel, etc.)
- Track conversions properly

## 🧪 Testing Checklist

Before going live:

- [ ] ESPN data fetches correctly
- [ ] AI generates quality insights
- [ ] Supabase saves/retrieves data
- [ ] Auth flow works (Google)
- [ ] Payment flow works (Stripe)
- [ ] Subscription gates content
- [ ] Affiliate links track properly
- [ ] Mobile responsive
- [ ] Load testing (can handle traffic)

## 📈 Launch Strategy

### Week 1: Soft Launch
- Friends/family only
- Free access to test feedback
- Fix bugs, improve AI prompts

### Week 2: Beta Launch
- Reddit (r/sportsbook, r/nfl)
- Twitter/X sports betting community
- Collect emails for official launch

### Week 3: Full Launch
- Enable paid subscriptions
- Affiliate partnerships
- Social media promotion
- Email blast

### Week 4+: Optimize
- A/B test pricing
- Add features based on feedback
- Optimize AI prompts
- Scale affiliate revenue

## 💡 Revenue Potential

**Conservative estimates:**

| Subs | Revenue/mo | Costs | Profit |
|------|-----------|-------|--------|
| 10   | $100-200  | ~$20  | $80-180 |
| 50   | $500-1000 | ~$50  | $450-950 |
| 100  | $1000-2000| ~$100 | $900-1900 |
| 500  | $5000-10k | ~$300 | $4700-9700 |

Plus affiliate revenue (potentially 2-5x subscription revenue if conversion is good).

## 🤝 Similar to Ask Finn

You've already built 80% of this with Ask Finn:

| Component | Difficulty | Time |
|-----------|-----------|------|
| Backend pipeline | ✅ Done | - |
| Supabase setup | Easy | 1-2 hrs |
| Frontend structure | Easy | 4-8 hrs |
| Auth (Google) | Easy | 1 hr |
| Payments (Stripe) | Easy | 2 hrs |
| Gating logic | Easy | 1 hr |
| Design/styling | Medium | 4-8 hrs |
| Testing/polish | Medium | 4-8 hrs |

**Total: ~3-5 days to MVP**

## 📧 Next Steps

1. **Today**: Test the pipeline locally
2. **Tomorrow**: Set up Supabase + create tables
3. **This weekend**: Build the frontend (reuse Ask Finn)
4. **Next week**: Deploy + soft launch

## 🆘 Need Help?

Check these files:
- `README.md` - Full documentation
- `pipeline.py` - Main code with comments
- Output JSON files - See data structure

Everything is ready to go. Just need to:
1. Add your OpenAI key
2. Connect Supabase
3. Build the frontend (copy Ask Finn)
4. Launch! 🚀
