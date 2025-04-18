'use client'

import { Box, Button, Container, Heading, Text, VStack, useColorModeValue } from '@chakra-ui/react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/providers/AuthProvider'

export default function Home() {
  const router = useRouter()
  const { user } = useAuth()
  const bgColor = useColorModeValue('gray.50', 'gray.900')
  const textColor = useColorModeValue('gray.600', 'gray.300')

  return (
    <Box bg={bgColor} minH="100vh" py={20}>
      <Container maxW="container.md">
        <VStack spacing={8} textAlign="center">
          <Heading
            as="h1"
            size="2xl"
            bgGradient="linear(to-r, blue.400, purple.500)"
            backgroundClip="text"
          >
            Fashion AI Assistant
          </Heading>

          <Text fontSize="xl" color={textColor} maxW="600px">
            Your personal AI-powered fashion assistant. Get personalized style recommendations,
            outfit suggestions, and stay up-to-date with the latest fashion trends.
          </Text>

          {!user ? (
            <Button
              size="lg"
              colorScheme="blue"
              onClick={() => router.push('/auth/login')}
              px={8}
            >
              Get Started
            </Button>
          ) : (
            <Button
              size="lg"
              colorScheme="blue"
              onClick={() => router.push('/account')}
              px={8}
            >
              Go to Dashboard
            </Button>
          )}

          <Box pt={10}>
            <Text fontSize="md" color={textColor}>
              ✨ Powered by advanced AI technology
            </Text>
            <Text fontSize="md" color={textColor}>
              🎯 Personalized recommendations based on your style
            </Text>
            <Text fontSize="md" color={textColor}>
              🔒 Secure authentication with Google or email
            </Text>
          </Box>
        </VStack>
      </Container>
    </Box>
  )
} 