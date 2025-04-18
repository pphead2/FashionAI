import { useCallback } from 'react'
import { useToast } from '@chakra-ui/toast'
import { AuthErrors } from '../utils/authErrors'

export function useAuthError() {
  const toast = useToast()

  const handleAuthError = useCallback((error: unknown) => {
    const { title, message } = AuthErrors.getErrorMessage(error)
    
    toast({
      title,
      description: message,
      status: 'error',
      duration: 5000,
      isClosable: true,
      position: 'top-right'
    })
  }, [toast])

  return { handleAuthError }
} 