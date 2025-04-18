'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Box, Button, Input, VStack, Text, Divider, useToast } from '@chakra-ui/react'
import { createClientComponentClient } from '@supabase/auth-helpers-nextjs'
import { useAuth } from '@/providers/AuthProvider'
import type { Database } from '@/lib/database.types'

export default function SignUp() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const router = useRouter()
  const { signUp } = useAuth()
  const toast = useToast()
  const supabase = createClientComponentClient<Database>()

  const handleEmailSignUp = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    if (password !== confirmPassword) {
      toast({
        title: 'Error',
        description: 'Passwords do not match',
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
      setLoading(false)
      return
    }
    
    try {
      await signUp(email, password)
      toast({
        title: 'Check your email',
        description: 'We sent you a verification link to complete your registration.',
        status: 'success',
        duration: 5000,
        isClosable: true,
      })
      router.push('/auth/login')
    } catch (error) {
      // Error will be handled by our error handler
    } finally {
      setLoading(false)
    }
  }

  const handleGoogleSignUp = async () => {
    try {
      setLoading(true)
      const { error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: `${window.location.origin}/auth/callback`,
          queryParams: {
            access_type: 'offline',
            prompt: 'consent',
          }
        }
      })

      if (error) throw error
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to sign up with Google. Please try again.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box>
      <VStack spacing={6} align="stretch">
        <Text fontSize="2xl" fontWeight="bold" textAlign="center">
          Create Account
        </Text>

        <form onSubmit={handleEmailSignUp}>
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
            <Input
              type="password"
              placeholder="Confirm Password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
            />
            <Button
              type="submit"
              colorScheme="blue"
              width="100%"
              isLoading={loading}
            >
              Sign Up with Email
            </Button>
          </VStack>
        </form>

        <Divider />

        <Button
          onClick={handleGoogleSignUp}
          variant="outline"
          width="100%"
          isLoading={loading}
        >
          Sign Up with Google
        </Button>

        <Text fontSize="sm" textAlign="center">
          Already have an account?{' '}
          <Button
            variant="link"
            colorScheme="blue"
            onClick={() => router.push('/auth/login')}
          >
            Sign In
          </Button>
        </Text>
      </VStack>
    </Box>
  )
} 