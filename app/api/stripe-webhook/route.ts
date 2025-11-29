import { NextRequest, NextResponse } from 'next/server'
import Stripe from 'stripe'
import { createClient } from '@supabase/supabase-js'

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2025-11-17.clover'
})

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
)

export async function POST(request: NextRequest) {
  const body = await request.text()
  const sig = request.headers.get('stripe-signature')!

  let event: Stripe.Event

  try {
    event = stripe.webhooks.constructEvent(
      body,
      sig,
      process.env.STRIPE_WEBHOOK_SECRET!
    )
  } catch (err: any) {
    console.error('Webhook signature verification failed:', err.message)
    return NextResponse.json({ error: 'Invalid signature' }, { status: 400 })
  }

  if (event.type === 'checkout.session.completed') {
    const session = event.data.object as Stripe.Checkout.Session
    const { userId, credits } = session.metadata!

    const { data: existing } = await supabase
      .from('user_credits')
      .select('balance')
      .eq('user_id', userId)
      .single()

    if (existing) {
      await supabase
        .from('user_credits')
        .update({
          balance: existing.balance + parseInt(credits),
          updated_at: new Date().toISOString()
        })
        .eq('user_id', userId)
    } else {
      await supabase
        .from('user_credits')
        .insert({
          user_id: userId,
          balance: parseInt(credits),
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        })
    }

    console.log(`Added ${credits} credits to user ${userId}`)
  }

  return NextResponse.json({ received: true })
}
