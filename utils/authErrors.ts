import { AuthError } from '@supabase/supabase-js'

export type AuthErrorType = 
  | 'InvalidEmail'
  | 'InvalidPassword'
  | 'EmailNotVerified'
  | 'EmailInUse'
  | 'WeakPassword'
  | 'InvalidCredentials'
  | 'NetworkError'
  | 'SessionExpired'
  | 'UnknownError'

interface ErrorMessage {
  title: string
  message: string
}

const errorMessages: Record<AuthErrorType, ErrorMessage> = {
  InvalidEmail: {
    title: 'Invalid Email',
    message: 'Please enter a valid email address.'
  },
  InvalidPassword: {
    title: 'Invalid Password',
    message: 'Password must be at least 8 characters long and include a number.'
  },
  EmailNotVerified: {
    title: 'Email Not Verified',
    message: 'Please verify your email address before signing in. Check your inbox for the verification link.'
  },
  EmailInUse: {
    title: 'Email Already Registered',
    message: 'This email is already registered. Please sign in or use a different email.'
  },
  WeakPassword: {
    title: 'Weak Password',
    message: 'Please choose a stronger password. Include numbers, special characters, and both upper and lowercase letters.'
  },
  InvalidCredentials: {
    title: 'Invalid Credentials',
    message: 'Incorrect email or password. Please try again.'
  },
  NetworkError: {
    title: 'Connection Error',
    message: 'Unable to connect to the server. Please check your internet connection and try again.'
  },
  SessionExpired: {
    title: 'Session Expired',
    message: 'Your session has expired. Please sign in again to continue.'
  },
  UnknownError: {
    title: 'Something Went Wrong',
    message: 'An unexpected error occurred. Please try again later.'
  }
}

export function getAuthErrorMessage(error: AuthError | Error | unknown): ErrorMessage {
  if (!error) {
    return errorMessages.UnknownError
  }

  // Handle Supabase AuthError
  if (error instanceof AuthError) {
    switch (error.message) {
      case 'Invalid login credentials':
        return errorMessages.InvalidCredentials
      case 'Email not confirmed':
        return errorMessages.EmailNotVerified
      case 'User already registered':
        return errorMessages.EmailInUse
      case 'Password should be at least 8 characters':
        return errorMessages.InvalidPassword
      default:
        return errorMessages.UnknownError
    }
  }

  // Handle network errors
  if (error instanceof Error && error.message.includes('network')) {
    return errorMessages.NetworkError
  }

  return errorMessages.UnknownError
}

export function isAuthError(error: unknown): error is AuthError {
  return error instanceof AuthError
}

export const AuthErrors = {
  getErrorMessage: getAuthErrorMessage,
  isAuthError,
  errorMessages
} 