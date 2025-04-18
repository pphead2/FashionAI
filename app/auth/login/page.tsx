'use client'

import { useState, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { Box, Button, Input, VStack, Text, Divider, useToast, Alert, AlertIcon } from '@chakra-ui/react'
import { createClientComponentClient } from '@supabase/auth-helpers-nextjs'
import { useAuth } from '@/providers/AuthProvider'
import type { Database } from '@/lib/database.types'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const router = useRouter()
  const searchParams = useSearchParams()
  const redirectTo = searchParams.get('redirect_to') || '/dashboard'
  const error = searchParams.get('error')
  const { signIn } = useAuth()
  const toast = useToast()
  const supabase = createClientComponentClient<Database>()

  // Check if user is already logged in
  useEffect(() => {
    const checkSession = async () => {
      const { data: { session } } = await supabase.auth.getSession()
      if (session) {
        router.replace('/dashboard')
      }
    }
    checkSession()
  }, [supabase.auth, router])

  const handleEmailSignIn = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    
    try {
      // Try direct sign in with Supabase client first
      const { data, error: signInError } = await supabase.auth.signInWithPassword({
        email,
        password
      })

      if (signInError) {
        throw signInError
      }

      if (data.session) {
        // Successfully signed in
        toast({
          title: 'Success',
          description: 'Successfully signed in',
          status: 'success',
          duration: 3000,
          isClosable: true,
        })
        router.replace('/dashboard')
      }
    } catch (error: any) {
      console.error('Sign in error:', error)
      toast({
        title: 'Error signing in',
        description: error.message || 'Failed to sign in. Please check your credentials.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
    } finally {
      setLoading(false)
    }
  }

  const handleGoogleSignIn = async () => {
    try {
      setLoading(true)
      const { data, error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: `${window.location.origin}/auth/callback?next=${encodeURIComponent('/dashboard')}`,
          queryParams: {
            access_type: 'offline',
            prompt: 'consent',
          }
        }
      })

      if (error) throw error
      
      // Google sign in initiated successfully
      toast({
        title: 'Google Sign In',
        description: 'Please complete the sign in process in the popup window',
        status: 'info',
        duration: 5000,
        isClosable: true,
      })
    } catch (error: any) {
      console.error('Google sign in error:', error)
      toast({
        title: 'Error',
        description: error.message || 'Failed to sign in with Google',
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box p={8} maxW="400px" mx="auto">
      <VStack spacing={6} align="stretch">
        <Text fontSize="2xl" fontWeight="bold" textAlign="center">
          Sign In
        </Text>

        {error && (
          <Alert status="error">
            <AlertIcon />
            {error}
          </Alert>
        )}

        <form onSubmit={handleEmailSignIn}>
          <VStack spacing={4}>
            <Input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <Input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <Button
              type="submit"
              colorScheme="blue"
              width="100%"
              isLoading={loading}
            >
              Sign In with Email
            </Button>
          </VStack>
        </form>

        <Divider />

        <Button
          onClick={handleGoogleSignIn}
          variant="outline"
          width="100%"
          isLoading={loading}
        >
          Sign In with Google
        </Button>

        <Text fontSize="sm" textAlign="center">
          Don't have an account?{' '}
          <Button
            variant="link"
            colorScheme="blue"
            onClick={() => router.push('/auth/signup')}
          >
            Sign Up
          </Button>
        </Text>

        <Button
          variant="link"
          colorScheme="blue"
          onClick={() => router.push('/auth/forgot-password')}
          alignSelf="center"
        >
          Forgot Password?
        </Button>
      </VStack>
    </Box>
  )
} 