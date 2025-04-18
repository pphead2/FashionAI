'use client'

import { Box, Container, useColorModeValue } from '@chakra-ui/react'
import { Providers } from '@/providers/Providers'

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  const bgColor = useColorModeValue('gray.50', 'gray.900')

  return (
    <Providers>
      <Box bg={bgColor} minH="100vh" py={20}>
        <Container maxW="container.sm">
          <Box
            bg={useColorModeValue('white', 'gray.800')}
            p={8}
            rounded="xl"
            shadow="lg"
          >
            {children}
          </Box>
        </Container>
      </Box>
    </Providers>
  )
} 