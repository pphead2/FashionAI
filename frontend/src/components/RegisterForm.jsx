import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useRouter } from 'next/router';
import { register } from '../store/authSlice';
import {
    Box,
    Button,
    TextField,
    Typography,
    Link,
    CircularProgress,
    Alert
} from '@mui/material';

const RegisterForm = () => {
    const dispatch = useDispatch();
    const router = useRouter();
    const { loading, error } = useSelector((state) => state.auth);

    const [formData, setFormData] = useState({
        email: '',
        password: '',
        confirmPassword: '',
        displayName: ''
    });

    const [formErrors, setFormErrors] = useState({});

    const validateForm = () => {
        const errors = {};
        if (formData.password !== formData.confirmPassword) {
            errors.confirmPassword = 'Passwords do not match';
        }
        if (formData.password.length < 8) {
            errors.password = 'Password must be at least 8 characters';
        }
        setFormErrors(errors);
        return Object.keys(errors).length === 0;
    };

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
        // Clear error when user starts typing
        if (formErrors[e.target.name]) {
            setFormErrors({
                ...formErrors,
                [e.target.name]: ''
            });
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!validateForm()) return;

        try {
            const { confirmPassword, ...registerData } = formData;
            await dispatch(register(registerData)).unwrap();
            router.push('/dashboard');
        } catch (err) {
            console.error('Registration failed:', err);
        }
    };

    return (
        <Box
            component="form"
            onSubmit={handleSubmit}
            sx={{
                display: 'flex',
                flexDirection: 'column',
                gap: 2,
                maxWidth: 400,
                mx: 'auto',
                p: 3
            }}
        >
            <Typography variant="h4" component="h1" gutterBottom>
                Create Account
            </Typography>

            {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                    {error}
                </Alert>
            )}

            <TextField
                required
                fullWidth
                id="email"
                label="Email Address"
                name="email"
                autoComplete="email"
                autoFocus
                value={formData.email}
                onChange={handleChange}
                disabled={loading}
                error={!!formErrors.email}
                helperText={formErrors.email}
            />

            <TextField
                required
                fullWidth
                id="displayName"
                label="Display Name"
                name="displayName"
                autoComplete="name"
                value={formData.displayName}
                onChange={handleChange}
                disabled={loading}
            />

            <TextField
                required
                fullWidth
                name="password"
                label="Password"
                type="password"
                id="password"
                autoComplete="new-password"
                value={formData.password}
                onChange={handleChange}
                disabled={loading}
                error={!!formErrors.password}
                helperText={formErrors.password}
            />

            <TextField
                required
                fullWidth
                name="confirmPassword"
                label="Confirm Password"
                type="password"
                id="confirmPassword"
                autoComplete="new-password"
                value={formData.confirmPassword}
                onChange={handleChange}
                disabled={loading}
                error={!!formErrors.confirmPassword}
                helperText={formErrors.confirmPassword}
            />

            <Button
                type="submit"
                fullWidth
                variant="contained"
                disabled={loading}
                sx={{ mt: 2 }}
            >
                {loading ? <CircularProgress size={24} /> : 'Register'}
            </Button>

            <Box sx={{ mt: 2, textAlign: 'center' }}>
                <Link href="/login" variant="body2">
                    Already have an account? Sign in
                </Link>
            </Box>
        </Box>
    );
};

export default RegisterForm; 