'use client'

import { useEffect, useState } from 'react'
import { createClientComponentClient } from '@supabase/auth-helpers-nextjs'
import { Button, Box, Typography, Container, Alert, CircularProgress } from '@mui/material'
import { useRouter } from 'next/navigation'
import type { Database } from '../../../lib/database.types'
import type { UserIdentity } from '@supabase/supabase-js'

export default function AccountLinking() {
  const router = useRouter()
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [currentUser, setCurrentUser] = useState<any>(null)
  const [linkedAccounts, setLinkedAccounts] = useState<UserIdentity[]>([])
  const supabase = createClientComponentClient<Database>()

  // Fetch current user and their linked accounts on mount
  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const { data: { session }, error: sessionError } = await supabase.auth.getSession()
        if (sessionError) throw sessionError

        if (!session) {
          // Redirect to login if no session
          router.push('/auth/login?redirectTo=/account/link')
          return
        }

        const { data: { user }, error: userError } = await supabase.auth.getUser()
        if (userError) throw userError

        setCurrentUser(user)
        
        // Get user's identities (linked accounts)
        const identities = user?.identities || []
        setLinkedAccounts(identities)
        
      } catch (err: any) {
        console.error('Error fetching user data:', err)
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    fetchUserData()

    // Set up auth state change listener
    const { data: { subscription } } = supabase.auth.onAuthStateChange(async (event, session) => {
      if (event === 'SIGNED_OUT') {
        router.push('/auth/login?redirectTo=/account/link')
      } else if (session?.user) {
        setCurrentUser(session.user)
        setLinkedAccounts(session.user.identities || [])
      }
    })

    return () => {
      subscription.unsubscribe()
    }
  }, [supabase.auth, router])

  const handleGoogleLink = async () => {
    try {
      setError(null)
      setSuccess(null)
      setLoading(true)

      const { data, error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: `${window.location.origin}/auth/callback`,
          queryParams: {
            // This tells Supabase to link the account instead of signing in
            prompt: 'consent',
            access_type: 'offline'
          }
        }
      })

      if (error) {
        console.error('OAuth error:', error)
        setError(error.message)
        return
      }

      if (data) {
        setSuccess('Account linking initiated. Please complete the process in the popup window.')
        console.log('OAuth data:', data)
      }
    } catch (err: any) {
      console.error('Unexpected error:', err)
      setError('An unexpected error occurred')
    } finally {
      setLoading(false)
    }
  }

  const handleUnlink = async (identity: UserIdentity) => {
    try {
      setError(null)
      setSuccess(null)
      setLoading(true)

      const { error } = await supabase.auth.unlinkIdentity(identity)

      if (error) {
        console.error('Unlink error:', error)
        setError(error.message)
        return
      }

      setSuccess(`Successfully unlinked ${identity.provider} account`)
      // Remove the identity from linkedAccounts
      setLinkedAccounts(prev => prev.filter(acc => acc.id !== identity.id))
    } catch (err: any) {
      console.error('Unexpected error:', err)
      setError('An unexpected error occurred')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <Container component="main" maxWidth="xs">
        <Box sx={{ mt: 8, display: 'flex', justifyContent: 'center' }}>
          <CircularProgress />
        </Box>
      </Container>
    )
  }

  if (!currentUser) {
    return (
      <Container component="main" maxWidth="xs">
        <Box sx={{ mt: 8, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
          <Typography variant="h6" color="error">
            Please sign in to access this page
          </Typography>
          <Button variant="contained" onClick={() => router.push('/auth/login?redirectTo=/account/link')}>
            Go to Login
          </Button>
        </Box>
      </Container>
    )
  }

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
          Account Linking
        </Typography>

        <Typography variant="body1" color="text.secondary">
          Primary Email: {currentUser.email}
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

        <Box sx={{ width: '100%', mt: 2 }}>
          <Typography variant="h6" gutterBottom>
            Linked Accounts
          </Typography>
          
          {linkedAccounts.length > 0 ? (
            linkedAccounts.map((identity) => (
              <Box key={identity.id} sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography>
                  {identity.provider.charAt(0).toUpperCase() + identity.provider.slice(1)}
                </Typography>
                <Button
                  variant="outlined"
                  color="error"
                  onClick={() => handleUnlink(identity)}
                  disabled={loading}
                >
                  Unlink
                </Button>
              </Box>
            ))
          ) : (
            <Typography color="text.secondary">
              No linked accounts
            </Typography>
          )}
        </Box>

        {!linkedAccounts.some(identity => identity.provider === 'google') && (
          <Button
            variant="contained"
            onClick={handleGoogleLink}
            disabled={loading}
            sx={{ mt: 2 }}
          >
            {loading ? 'Linking...' : 'Link Google Account'}
          </Button>
        )}
      </Box>
    </Container>
  )
} 