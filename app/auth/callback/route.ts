import { createRouteHandlerClient } from '@supabase/auth-helpers-nextjs'
import { cookies } from 'next/headers'
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import type { Database } from '@/lib/database.types'

export async function GET(request: NextRequest) {
  const requestUrl = new URL(request.url)
  const code = requestUrl.searchParams.get('code')
  const next = requestUrl.searchParams.get('next') || '/dashboard'

  if (code) {
    const cookieStore = cookies()
    const supabase = createRouteHandlerClient<Database>({ cookies: () => cookieStore })

    try {
      // Exchange the code for a session
      const { error } = await supabase.auth.exchangeCodeForSession(code)
      if (error) throw error

      // Get the session to confirm it worked
      const { data: { session }, error: sessionError } = await supabase.auth.getSession()
      if (sessionError) throw sessionError

      if (!session) {
        throw new Error('No session found after exchange')
      }

      // Successful authentication
      return NextResponse.redirect(new URL(next, requestUrl.origin))
    } catch (error: any) {
      console.error('Auth callback error:', error)
      // Redirect to login with error message
      return NextResponse.redirect(
        new URL(
          `/auth/login?error=${encodeURIComponent(error.message || 'Authentication failed')}`,
          requestUrl.origin
        )
      )
    }
  }

  // No code found, redirect to login
  return NextResponse.redirect(
    new URL('/auth/login?error=No authentication code found', requestUrl.origin)
  )
} 