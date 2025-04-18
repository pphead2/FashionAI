'use client'

import { Box, Button, Container, Heading, Text, VStack, Code, useToast } from '@chakra-ui/react'
import { useAuth } from '@/providers/AuthProvider'
import { useRouter } from 'next/navigation'
import { useState, useEffect } from 'react'
import { supabase } from '@/lib/supabaseClient'
import { User, UserIdentity } from '@supabase/supabase-js'

export default function Dashboard() {
  const { user, signOut } = useAuth()
  const router = useRouter()
  const toast = useToast()
  const [linkedAccounts, setLinkedAccounts] = useState<string[]>([])

  useEffect(() => {
    const fetchLinkedAccounts = async () => {
      const { data, error } = await supabase.auth.getUser()
      if (error || !data.user) {
        console.error('Error fetching user identities:', error)
        return
      }
      const identities = data.user.identities || []
      setLinkedAccounts(identities.map((identity: UserIdentity) => identity.provider))
    }

    fetchLinkedAccounts()
  }, [])

  const handleSignOut = async () => {
    try {
      await signOut()
      router.push('/')
    } catch (error) {
      toast({
        title: 'Error signing out',
        description: 'Please try again',
        status: 'error',
        duration: 3000,
        isClosable: true,
      })
    }
  }

  return (
    <Container maxW="container.xl" py={8}>
      {/* Header with Logout */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={8}>
        <Heading size="lg">Dashboard</Heading>
        <Button colorScheme="red" onClick={handleSignOut}>
          Logout
        </Button>
      </Box>

      {/* Upload Placeholder */}
      <Box
        border="2px dashed"
        borderColor="gray.300"
        borderRadius="lg"
        p={8}
        mb={8}
        textAlign="center"
      >
        <VStack spacing={4}>
          <Heading size="md">Upload Your Outfit</Heading>
          <Text color="gray.500">Coming Soon</Text>
        </VStack>
      </Box>

      {/* Debug Information */}
      <Box
        bg="gray.50"
        p={4}
        borderRadius="md"
        border="1px solid"
        borderColor="gray.200"
      >
        <Heading size="sm" mb={4}>Debug Information</Heading>
        <VStack align="stretch" spacing={2}>
          <Text><strong>User ID:</strong> {user?.id}</Text>
          <Text><strong>Email:</strong> {user?.email}</Text>
          <Text><strong>Last Sign In:</strong> {new Date(user?.last_sign_in_at || '').toLocaleString()}</Text>
          <Text><strong>Linked Accounts:</strong></Text>
          <Code p={2}>
            {linkedAccounts.length > 0 
              ? linkedAccounts.join(', ')
              : 'No linked accounts'
            }
          </Code>
        </VStack>
      </Box>
    </Container>
  )
} 