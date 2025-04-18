'use client'

import { useEffect, useState } from 'react'
import { createClientComponentClient } from '@supabase/auth-helpers-nextjs'
import { Button, Box, Typography, Container, Alert } from '@mui/material'
import type { Database } from '../../../lib/database.types'

export default function TestOAuth() {
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const supabase = createClientComponentClient<Database>()

  const handleGoogleSignIn = async () => {
    try {
      setError(null)
      setSuccess(null)
      setLoading(true)

      const redirectTo = `${window.location.origin}/auth/callback`
      console.log('Redirect URL:', redirectTo) // Debug log

      const { data, error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo,
          queryParams: {
            access_type: 'offline',
            prompt: 'consent',
          }
        }
      })

      if (error) {
        console.error('OAuth error:', error)
        setError(error.message)
        return
      }

      if (data) {
        setSuccess('OAuth flow initiated successfully')
        console.log('OAuth data:', data)
      }
    } catch (err) {
      console.error('Unexpected error:', err)
      setError('An unexpected error occurred')
    } finally {
      setLoading(false)
    }
  }

  // Listen for auth state changes
  useEffect(() => {
    const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => {
      console.log('Auth event:', event)
      console.log('Session:', session)
      
      if (event === 'SIGNED_IN') {
        setSuccess('Successfully signed in!')
      }
    })

    return () => {
      subscription.unsubscribe()
    }
  }, [supabase.auth])

  return (
    <Container component="main" maxWidth="xs">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: 2
        }}
      >
        <Typography component="h1" variant="h5">
          Test Google OAuth
        </Typography>

        {error && (
          <Alert severity="error" sx={{ width: '100%' }}>
            {error}
          </Alert>
        )}

        {success && (
          <Alert severity="success" sx={{ width: '100%' }}>
            {success}
          </Alert>
        )}

        <Button
          variant="contained"
          onClick={handleGoogleSignIn}
          disabled={loading}
          sx={{ mt: 2 }}
        >
          {loading ? 'Signing in...' : 'Sign in with Google'}
        </Button>

        <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
          Debug Info:
          <br />
          Current Origin: {typeof window !== 'undefined' ? window.location.origin : 'N/A'}
        </Typography>
      </Box>
    </Container>
  )
} 