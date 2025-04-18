'use client'

import { useState } from 'react'
import { Box, Button, Input, VStack, Text } from '@chakra-ui/react'
import { useToast } from '@chakra-ui/toast'
import { useAuth } from '../providers/AuthProvider'

export function AuthTest() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const { user, signIn, signUp, signOut, resetPassword } = useAuth()
  const toast = useToast()

  const handleSignUp = async () => {
    try {
      await signUp(email, password)
      toast({
        title: 'Check your email',
        description: 'We sent you a verification link to complete your registration.',
        status: 'success',
        duration: 5000,
        isClosable: true,
      })
    } catch (error) {
      // Error will be handled by our error handler
    }
  }

  const handleSignIn = async () => {
    try {
      await signIn(email, password)
      toast({
        title: 'Welcome back!',
        status: 'success',
        duration: 3000,
        isClosable: true,
      })
    } catch (error) {
      // Error will be handled by our error handler
    }
  }

  const handleSignOut = async () => {
    try {
      await signOut()
      toast({
        title: 'Signed out successfully',
        status: 'info',
        duration: 3000,
        isClosable: true,
      })
    } catch (error) {
      // Error will be handled by our error handler
    }
  }

  const handleResetPassword = async () => {
    try {
      await resetPassword(email)
      toast({
        title: 'Check your email',
        description: 'We sent you a password reset link.',
        status: 'success',
        duration: 5000,
        isClosable: true,
      })
    } catch (error) {
      // Error will be handled by our error handler
    }
  }

  return (
    <Box p={4} maxW="400px" mx="auto">
      <VStack gap={4} alignItems="stretch">
        <Text fontSize="xl" fontWeight="bold">
          {user ? `Welcome, ${user.email}` : 'Authentication Test'}
        </Text>

        {!user ? (
          <>
            <Input
              placeholder="Email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            <Input
              placeholder="Password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <Button onClick={handleSignUp} colorScheme="green">
              Sign Up
            </Button>
            <Button onClick={handleSignIn} colorScheme="blue">
              Sign In
            </Button>
            <Button onClick={handleResetPassword} variant="ghost">
              Reset Password
            </Button>
          </>
        ) : (
          <Button onClick={handleSignOut} colorScheme="red">
            Sign Out
          </Button>
        )}

        {/* Debug Information */}
        {user && (
          <Box mt={4} p={4} bg="gray.50" borderRadius="md">
            <Text fontSize="sm" fontWeight="bold">Debug Info:</Text>
            <Text fontSize="xs">User ID: {user.id}</Text>
            <Text fontSize="xs">Email: {user.email}</Text>
            <Text fontSize="xs">Email Verified: {String(user.email_confirmed_at !== null)}</Text>
          </Box>
        )}
      </VStack>
    </Box>
  )
} 