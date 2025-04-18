'use client'

import { useEffect, useState } from 'react'
import { createClientComponentClient } from '@supabase/auth-helpers-nextjs'
import { useRouter, useSearchParams } from 'next/navigation'
import type { Database } from '../../../lib/database.types'
import { Button, TextField, Box, Typography, Container, Alert, CircularProgress } from '@mui/material'

export default function ResetPassword() {
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)
  const [loading, setLoading] = useState(false)
  const [initializing, setInitializing] = useState(true)
  const router = useRouter()
  const searchParams = useSearchParams()
  const supabase = createClientComponentClient<Database>()

  // Handle the initial token verification
  useEffect(() => {
    const setupSession = async () => {
      try {
        // Get all tokens from the URL
        const code = searchParams.get('code')
        const type = searchParams.get('type')

        if (!code || type !== 'recovery') {
          setError('Invalid or missing reset token. Please use the complete link from your email.')
          setInitializing(false)
          return
        }

        // Verify the recovery token
        const { error } = await supabase.auth.verifyOtp({
          token_hash: code,
          type: 'recovery'
        })
        
        if (error) {
          console.error('Token verification error:', error)
          setError('Invalid or expired reset token. Please request a new password reset link.')
          setInitializing(false)
          return
        }

        setInitializing(false)
      } catch (err) {
        console.error('Reset token verification error:', err)
        setError('An error occurred while verifying your reset token.')
        setInitializing(false)
      }
    }

    setupSession()
  }, [searchParams, supabase.auth])

  const handlePasswordReset = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    if (password !== confirmPassword) {
      setError('Passwords do not match')
      setLoading(false)
      return
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters long')
      setLoading(false)
      return
    }

    try {
      const { error } = await supabase.auth.updateUser({ password })

      if (error) {
        setError(error.message)
      } else {
        setSuccess(true)
        // Redirect to login page after 3 seconds
        setTimeout(() => {
          router.push('/auth/login')
        }, 3000)
      }
    } catch (err) {
      setError('An error occurred while resetting your password')
    } finally {
      setLoading(false)
    }
  }

  if (initializing) {
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
          <CircularProgress />
          <Typography>
            Verifying your reset token...
          </Typography>
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
        }}
      >
        <Typography component="h1" variant="h5" sx={{ mb: 3 }}>
          Reset Your Password
        </Typography>

        {error && (
          <Alert severity="error" sx={{ width: '100%', mb: 2 }}>
            {error}
          </Alert>
        )}

        {success ? (
          <Alert severity="success" sx={{ width: '100%', mb: 2 }}>
            Password successfully reset! Redirecting to login...
          </Alert>
        ) : (
          <Box component="form" onSubmit={handlePasswordReset} sx={{ mt: 1, width: '100%' }}>
            <TextField
              margin="normal"
              required
              fullWidth
              name="password"
              label="New Password"
              type="password"
              id="password"
              autoComplete="new-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={loading}
            />
            <TextField
              margin="normal"
              required
              fullWidth
              name="confirmPassword"
              label="Confirm New Password"
              type="password"
              id="confirmPassword"
              autoComplete="new-password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              disabled={loading}
            />
            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2 }}
              disabled={loading}
            >
              {loading ? 'Resetting Password...' : 'Reset Password'}
            </Button>
          </Box>
        )}
      </Box>
    </Container>
  )
} 