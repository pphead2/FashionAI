import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create axios instance with credentials
const api = axios.create({
    baseURL: API_URL,
    withCredentials: true,
    headers: {
        'Content-Type': 'application/json'
    }
});

// Add token to requests if available
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Refresh token on 401 errors
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;
        if (error.response.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;
            try {
                const response = await api.post('/auth/refresh');
                const { access_token } = response.data;
                localStorage.setItem('token', access_token);
                originalRequest.headers.Authorization = `Bearer ${access_token}`;
                return api(originalRequest);
            } catch (error) {
                // Refresh failed, redirect to login
                localStorage.removeItem('token');
                window.location.href = '/login';
                return Promise.reject(error);
            }
        }
        return Promise.reject(error);
    }
);

const authService = {
    async register(userData) {
        const response = await api.post('/auth/register', userData);
        if (response.data.access_token) {
            localStorage.setItem('token', response.data.access_token);
        }
        return response.data;
    },

    async login(credentials) {
        const response = await api.post('/auth/login', credentials);
        if (response.data.access_token) {
            localStorage.setItem('token', response.data.access_token);
        }
        return response.data;
    },

    async logout() {
        await api.post('/auth/logout');
        localStorage.removeItem('token');
    },

    async getProfile() {
        const response = await api.get('/profile/me');
        return response.data;
    },

    async updateProfile(profileData) {
        const response = await api.put('/profile/me', profileData);
        return response.data;
    },

    async uploadProfileImage(file) {
        const formData = new FormData();
        formData.append('file', file);
        const response = await api.post('/profile/me/image', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });
        return response.data;
    },

    async changePassword(passwordData) {
        const response = await api.post('/auth/change-password', passwordData);
        return response.data;
    },

    async changeEmail(emailData) {
        const response = await api.post('/auth/change-email', emailData);
        return response.data;
    },

    async requestPasswordReset(email) {
        const response = await api.post('/auth/request-password-reset', { email });
        return response.data;
    },

    async refresh() {
        const response = await api.post('/auth/refresh');
        if (response.data.access_token) {
            localStorage.setItem('token', response.data.access_token);
        }
        return response.data;
    }
};

export default authService; 