import { createMiddlewareClient } from '@supabase/auth-helpers-nextjs'
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import type { Database } from '@/lib/database.types'

// List of paths that require authentication
const PROTECTED_PATHS = [
  '/dashboard',
  '/account',
  '/profile',
]

// List of paths that should redirect to dashboard if user is already authenticated
const AUTH_PATHS = [
  '/auth/login',
  '/auth/signup',
]

export async function middleware(request: NextRequest) {
  const res = NextResponse.next()
  const supabase = createMiddlewareClient<Database>({ req: request, res })
  
  try {
    // Refresh session if expired
    await supabase.auth.getSession()

    const {
      data: { session },
    } = await supabase.auth.getSession()

    const requestPath = new URL(request.url).pathname

    // Check if the path requires authentication
    const isProtectedPath = PROTECTED_PATHS.some(path => requestPath.startsWith(path))
    const isAuthPath = AUTH_PATHS.some(path => requestPath.startsWith(path))

    if (isProtectedPath && !session) {
      // Redirect to login if accessing protected route without session
      const redirectUrl = new URL('/auth/login', request.url)
      redirectUrl.searchParams.set('next', requestPath)
      return NextResponse.redirect(redirectUrl)
    }

    if (isAuthPath && session) {
      // Redirect to dashboard if accessing auth routes with active session
      return NextResponse.redirect(new URL('/dashboard', request.url))
    }

    return res
  } catch (e) {
    // Handle any errors by redirecting to login
    console.error('Middleware error:', e)
    return NextResponse.redirect(new URL('/auth/login', request.url))
  }
}

export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder
     */
    '/((?!_next/static|_next/image|favicon.ico|public/).*)',
  ],
} 