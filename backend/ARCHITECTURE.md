# NFL Betting Platform - Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         DAILY PIPELINE                               │
│                       (Runs at 3 AM Daily)                          │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
         ┌──────────────────────────────────────────────┐
         │  1. FETCH ESPN DATA                          │
         │  ────────────────────                        │
         │  • Current week's games                      │
         │  • Team records                              │
         │  • Odds (spread, O/U, ML)                    │
         │  • Venue info                                │
         │                                              │
         │  ESPN API:                                   │
         │  site.api.espn.com/apis/site/v2/sports/...  │
         └──────────────────────────────────────────────┘
                                    │
                                    ▼
         ┌──────────────────────────────────────────────┐
         │  2. EXTRACT & STRUCTURE                      │
         │  ───────────────────────                     │
         │  Parse ESPN's messy JSON into:               │
         │                                              │
         │  {                                           │
         │    "game_id": "401671890",                   │
         │    "home_team": {...},                       │
         │    "away_team": {...},                       │
         │    "odds": {...},                            │
         │    "venue": {...}                            │
         │  }                                           │
         └──────────────────────────────────────────────┘
                                    │
                                    ▼
         ┌──────────────────────────────────────────────┐
         │  3. AI ANALYSIS                              │
         │  ────────────────                            │
         │  For each game, send to OpenAI:              │
         │                                              │
         │  Prompt: "Analyze this matchup..."           │
         │           + Game data                        │
         │           + Betting lines                    │
         │                                              │
         │  Response:                                   │
         │  • Top insight                               │
         │  • Summary (2-3 paragraphs)                  │
         │  • AI lean (spread/total)                    │
         │  • 3-5 angles                                │
         │  • Predicted line/total                      │
         │  • Team strength ratings                     │
         │  • Injury impact                             │
         │  • Confidence score                          │
         │                                              │
         │  Cost: ~$0.10-0.20 per game                  │
         └──────────────────────────────────────────────┘
                                    │
                                    ▼
         ┌──────────────────────────────────────────────┐
         │  4. SAVE TO DATABASE                         │
         │  ─────────────────────                       │
         │  Supabase Postgres:                          │
         │                                              │
         │  ┌──────────────────┐                        │
         │  │ games_raw        │                        │
         │  ├──────────────────┤                        │
         │  │ game_id          │                        │
         │  │ raw_json         │ ◄── ESPN data          │
         │  │ fetched_at       │                        │
         │  └──────────────────┘                        │
         │                                              │
         │  ┌──────────────────┐                        │
         │  │ ai_outputs       │                        │
         │  ├──────────────────┤                        │
         │  │ game_id          │                        │
         │  │ top_insight      │ ◄── AI analysis        │
         │  │ summary          │                        │
         │  │ ai_lean          │                        │
         │  │ angles           │                        │
         │  │ predicted_line   │                        │
         │  │ team_strength    │                        │
         │  │ ...              │                        │
         │  └──────────────────┘                        │
         └──────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (Next.js)                           │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
                    ▼                               ▼
         ┌─────────────────────┐         ┌─────────────────────┐
         │  HOMEPAGE (/)        │         │  GAME PAGE          │
         │  ─────────────       │         │  (/game/[id])       │
         │                     │         │  ─────────────       │
         │  • List today's      │         │                     │
         │    games             │         │  FREE (no login):   │
         │  • Show matchups     │         │  • Top insight      │
         │  • Quick preview     │         │  • Summary preview  │
         │    of insights       │         │  • Blurred angles   │
         │                     │         │                     │
         │  API: /api/games     │         │  PAID (subscriber): │
         │                     │         │  • Full summary     │
         │  [Game 1 Card] ─┐   │         │  • AI lean          │
         │  [Game 2 Card] ─┤───┼────────▶│  • All angles       │
         │  [Game 3 Card] ─┘   │         │  • Predictions      │
         │                     │         │  • Team strength    │
         │  [Sign Up CTA]      │         │  • Confidence       │
         └─────────────────────┘         │                     │
                                         │  [Affiliate CTA]    │
                                         │  [Affiliate CTA]    │
                                         │  [Affiliate CTA]    │
                                         └─────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                    AUTH & SUBSCRIPTIONS                              │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
                    ▼                               ▼
         ┌─────────────────────┐         ┌─────────────────────┐
         │  SUPABASE AUTH       │         │  STRIPE PAYMENTS     │
         │  ──────────────      │         │  ────────────────    │
         │                     │         │                     │
         │  • Google Sign-In   │         │  • Monthly plan     │
         │  • Session mgmt     │         │  • $10-20/mo        │
         │  • User profiles    │         │  • Webhook handler  │
         │                     │         │  • Update DB        │
         │  Copy from           │         │                     │
         │  Ask Finn ✅         │         │  Copy from          │
         │                     │         │  Ask Finn ✅         │
         └─────────────────────┘         └─────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                         MONETIZATION                                 │
└─────────────────────────────────────────────────────────────────────┘

    ┌──────────────────┐              ┌──────────────────┐
    │  SUBSCRIPTIONS   │              │  AFFILIATES       │
    │  ──────────────   │              │  ──────────       │
    │                  │              │                  │
    │  $10-20/month    │              │  DraftKings      │
    │  Full access     │              │  FanDuel         │
    │  Predictions     │              │  BetMGM          │
    │  Angles          │              │  Caesars         │
    │                  │              │                  │
    │  Target: 100     │              │  Commission:     │
    │  subs = $1-2k/mo │              │  $50-200 CPA     │
    └──────────────────┘              └──────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                         DATA FLOW                                    │
└─────────────────────────────────────────────────────────────────────┘

 3:00 AM Daily
     │
     ▼
  ┌──────┐
  │ CRON │ ──────▶ [Fetch ESPN] ──────▶ [Extract Data]
  └──────┘                                      │
                                               ▼
                                          [AI Analysis]
                                               │
                                               ▼
                                         [Save to DB]
                                               │
                                               ▼
                              ┌────────────────────────────┐
                              │     Supabase Database      │
                              │  (Ready for frontend API)  │
                              └────────────────────────────┘
                                               │
                                               ▼
                              User visits site at 10 AM
                                               │
                                               ▼
                              Frontend fetches pre-generated
                                   analysis (instant!)

┌─────────────────────────────────────────────────────────────────────┐
│                      TECH STACK                                      │
└─────────────────────────────────────────────────────────────────────┘

 Backend Pipeline:              Frontend:                
 ─────────────────              ─────────                
 • Python 3.12                  • Next.js 14             
 • OpenAI API                   • React                  
 • Requests                     • Tailwind CSS           
 • Schedule/Cron                • SWR                    
                                • TypeScript             
                                                         
 Database:                      Auth & Payments:         
 ─────────                      ────────────────         
 • Supabase                     • Supabase Auth          
 • PostgreSQL                   • Stripe                 
 • Row Level Security           • Google OAuth           
                                                         
 Deployment:                                             
 ───────────                                             
 • Vercel (frontend)                                     
 • DigitalOcean (pipeline)                               
 • Vercel Cron (optional)                                

┌─────────────────────────────────────────────────────────────────────┐
│                      COST BREAKDOWN                                  │
└─────────────────────────────────────────────────────────────────────┘

 OpenAI:                        Infrastructure:          
 ───────                        ──────────────          
 • $8-12/month                  • Supabase: Free tier   
 • gpt-4o-mini                  • Vercel: Free tier     
 • ~16 games/week               • Domain: $10/year      
 • $0.10-0.20/game                                       
                                                         
 TOTAL: ~$10-15/month                                    
                                                         
 Revenue (100 subs):                                     
 $1000-2000/month                                        
                                                         
 Profit margin: 98%+                                     
```
