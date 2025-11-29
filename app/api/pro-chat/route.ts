import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
)

const SPREAD_EDUCATION = `
UNDERSTANDING NFL SPREADS (CRITICAL):

The spread represents the expected margin of victory.
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

Focus on MARGIN OF VICTORY relative to the line, not just who wins.
`

export async function POST(request: NextRequest) {
  try {
    const { query, userId } = await request.json()

    if (!query || !userId) {
      return NextResponse.json(
        { error: 'Missing query or userId' },
        { status: 400 }
      )
    }

    // Check credits
    const { data: userCredits } = await supabase
      .from('user_credits')
      .select('balance')
      .eq('user_id', userId)
      .single()

    if (!userCredits || userCredits.balance < 10) {
      return NextResponse.json(
        { error: 'Insufficient credits' },
        { status: 402 }
      )
    }

    // Deduct 10 credits
    await supabase
      .from('user_credits')
      .update({
        balance: userCredits.balance - 10,
        updated_at: new Date().toISOString()
      })
      .eq('user_id', userId)

    // Fetch this week's NFL games from database
    const { data: games } = await supabase
      .from('games_raw')
      .select('*')
      .order('game_time', { ascending: true })
      .limit(30)

    // Fetch AI analysis from database
    const { data: aiOutputs } = await supabase
      .from('ai_outputs')
      .select('*')
      .order('created_at', { ascending: false })
      .limit(10)

    // Build context with actual NFL data
    let nflContext = '\n\n=== CURRENT WEEK NFL GAMES ===\n\n'
    
    if (games && games.length > 0) {
      const upcomingGames = games.filter((g: any) => g.raw_json?.status === 'pre')
      const completedGames = games.filter((g: any) => g.raw_json?.status === 'post')
      
      if (upcomingGames.length > 0) {
        nflContext += '** UPCOMING GAMES **\n'
        upcomingGames.forEach((game: any) => {
          const away = game.raw_json.away_team
          const home = game.raw_json.home_team
          const odds = game.raw_json.odds
          
          nflContext += `\n${away.name} (${away.record}) @ ${home.name} (${home.record})`
          nflContext += `\nTime: ${game.raw_json.game_time_display}`
          
          if (odds) {
            nflContext += `\nSpread: ${odds.spread}`
            nflContext += `\nOver/Under: ${odds.over_under}`
            nflContext += `\nMoneyline: Away ${odds.away_moneyline}, Home ${odds.home_moneyline}`
          }
          nflContext += '\n'
        })
      }
      
      if (completedGames.length > 0) {
        nflContext += '\n** RECENT RESULTS **\n'
        completedGames.slice(0, 5).forEach((game: any) => {
          const away = game.raw_json.away_team
          const home = game.raw_json.home_team
          nflContext += `\n${away.name} ${away.score} @ ${home.name} ${home.score} (Final)`
        })
      }
    }

    if (aiOutputs && aiOutputs.length > 0) {
      nflContext += '\n\n=== AI BETTING INSIGHTS ===\n'
      aiOutputs.slice(0, 3).forEach((output: any) => {
        if (output.betting_analysis) {
          nflContext += `\n${output.game_matchup}:\n${output.betting_analysis.substring(0, 300)}...\n`
        }
      })
    }

    const enhancedQuery = `${query}\n\nUSE THE FOLLOWING REAL NFL DATA TO ANSWER:\n${nflContext}`

    // Multi-model AI responses
    const [response1, response2, response3] = await Promise.allSettled([
      fetchOpenAI(enhancedQuery),
      fetchClaude(enhancedQuery),
      fetchGemini(enhancedQuery)
    ])

    // Combine responses
    let combinedResponse = ''
    const models = []

    if (response1.status === 'fulfilled') {
      combinedResponse += `## Advanced Analytics Engine\n\n${response1.value}\n\n`
      models.push('Advanced Analytics')
    }

    if (response2.status === 'fulfilled') {
      combinedResponse += `## Deep Learning Analysis\n\n${response2.value}\n\n`
      models.push('Deep Learning')
    }

    if (response3.status === 'fulfilled') {
      combinedResponse += `## Neural Network Insights\n\n${response3.value}\n\n`
      models.push('Neural Network')
    }

    if (models.length === 0) {
      // Refund credits if all models failed
      await supabase
        .from('user_credits')
        .update({
          balance: userCredits.balance,
          updated_at: new Date().toISOString()
        })
        .eq('user_id', userId)
      
      throw new Error('All AI models failed to respond')
    }

    return NextResponse.json({
      response: combinedResponse,
      models: ['Multi-Model AI Fusion']
    })

  } catch (error: any) {
    console.error('Pro chat error:', error)
    return NextResponse.json(
      { error: error.message || 'Internal server error' },
      { status: 500 }
    )
  }
}

async function fetchOpenAI(query: string): Promise<string> {
  const apiKey = process.env.OPENAI_API_KEY
  if (!apiKey) throw new Error('OpenAI API key not configured')

  const response = await fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${apiKey}`
    },
    body: JSON.stringify({
      model: 'gpt-4o-mini',
      messages: [
        {
          role: 'system',
          content: `You are an expert NFL betting analyst specializing in point spread analysis.

${SPREAD_EDUCATION}

Analyze the REAL current week games provided. Reference actual teams, spreads, and records. Give specific, actionable betting insights focused on spread coverage, not just picking winners.`
        },
        {
          role: 'user',
          content: query
        }
      ],
      max_tokens: 800,
      temperature: 0.7
    })
  })

  if (!response.ok) {
    throw new Error('OpenAI API failed')
  }

  const data = await response.json()
  return data.choices[0].message.content
}

async function fetchClaude(query: string): Promise<string> {
  const apiKey = process.env.ANTHROPIC_API_KEY
  if (!apiKey) throw new Error('Claude API key not configured')

  const response = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': apiKey,
      'anthropic-version': '2023-06-01'
    },
    body: JSON.stringify({
      model: 'claude-3-5-sonnet-20241022',
      max_tokens: 800,
      messages: [
        {
          role: 'user',
          content: `You are an expert NFL betting analyst specializing in point spread analysis.

${SPREAD_EDUCATION}

Use the REAL game data with actual spreads and team records. Focus on margin of victory and spread coverage, not just picking winners. ${query}`
        }
      ]
    })
  })

  if (!response.ok) {
    throw new Error('Claude API failed')
  }

  const data = await response.json()
  return data.content[0].text
}

async function fetchGemini(query: string): Promise<string> {
  const apiKey = process.env.GEMINI_API_KEY
  if (!apiKey) throw new Error('Gemini API key not configured')

  const response = await fetch(
    `https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=${apiKey}`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        contents: [{
          parts: [{
            text: `You are an expert NFL betting analyst specializing in point spread analysis.

${SPREAD_EDUCATION}

Use the REAL game data provided. Focus on spread coverage and margin of victory, not just picking winners. ${query}`
          }]
        }]
      })
    }
  )

  if (!response.ok) {
    throw new Error('Gemini API failed')
  }

  const data = await response.json()
  return data.candidates[0].content.parts[0].text
}
