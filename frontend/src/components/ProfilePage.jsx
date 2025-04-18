import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
    Box,
    Button,
    TextField,
    Typography,
    Avatar,
    CircularProgress,
    Alert,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
} from '@mui/material';
import { getProfile } from '../store/authSlice';
import authService from '../services/authService';

const ProfilePage = () => {
    const dispatch = useDispatch();
    const { user, loading } = useSelector((state) => state.auth);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);
    const [isEditing, setIsEditing] = useState(false);
    const [showDeleteDialog, setShowDeleteDialog] = useState(false);
    const [formData, setFormData] = useState({
        display_name: '',
        bio: '',
    });

    useEffect(() => {
        if (user) {
            setFormData({
                display_name: user.display_name || '',
                bio: user.bio || '',
            });
        }
    }, [user]);

    useEffect(() => {
        dispatch(getProfile());
    }, [dispatch]);

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await authService.updateProfile(formData);
            await dispatch(getProfile());
            setSuccess('Profile updated successfully');
            setIsEditing(false);
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to update profile');
        }
    };

    const handleImageUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        try {
            await authService.uploadProfileImage(file);
            await dispatch(getProfile());
            setSuccess('Profile image updated successfully');
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to upload image');
        }
    };

    const handleDeleteAccount = async () => {
        try {
            await authService.deleteAccount();
            // Redirect to login or home page after successful deletion
            window.location.href = '/login';
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to delete account');
            setShowDeleteDialog(false);
        }
    };

    if (loading) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
                <CircularProgress />
            </Box>
        );
    }

    return (
        <Box sx={{ maxWidth: 600, mx: 'auto', p: 3 }}>
            <Typography variant="h4" component="h1" gutterBottom>
                Profile
            </Typography>

            {error && (
                <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
                    {error}
                </Alert>
            )}

            {success && (
                <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>
                    {success}
                </Alert>
            )}

            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mb: 4 }}>
                <input
                    accept="image/*"
                    style={{ display: 'none' }}
                    id="profile-image-upload"
                    type="file"
                    onChange={handleImageUpload}
                />
                <label htmlFor="profile-image-upload">
                    <Avatar
                        src={user?.image_url}
                        sx={{ width: 120, height: 120, mb: 2, cursor: 'pointer' }}
                    />
                </label>
                <Typography variant="body2" color="textSecondary">
                    Click the avatar to upload a new image
                </Typography>
            </Box>

            <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <TextField
                    fullWidth
                    label="Display Name"
                    name="display_name"
                    value={formData.display_name}
                    onChange={handleChange}
                    disabled={!isEditing}
                />

                <TextField
                    fullWidth
                    label="Bio"
                    name="bio"
                    value={formData.bio}
                    onChange={handleChange}
                    multiline
                    rows={4}
                    disabled={!isEditing}
                />

                {isEditing ? (
                    <Box sx={{ display: 'flex', gap: 2 }}>
                        <Button type="submit" variant="contained" color="primary">
                            Save Changes
                        </Button>
                        <Button variant="outlined" onClick={() => setIsEditing(false)}>
                            Cancel
                        </Button>
                    </Box>
                ) : (
                    <Button variant="contained" onClick={() => setIsEditing(true)}>
                        Edit Profile
                    </Button>
                )}

                <Button
                    variant="outlined"
                    color="error"
                    onClick={() => setShowDeleteDialog(true)}
                    sx={{ mt: 4 }}
                >
                    Delete Account
                </Button>
            </Box>

            <Dialog open={showDeleteDialog} onClose={() => setShowDeleteDialog(false)}>
                <DialogTitle>Delete Account</DialogTitle>
                <DialogContent>
                    <Typography>
                        Are you sure you want to delete your account? This action cannot be undone.
                    </Typography>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setShowDeleteDialog(false)}>Cancel</Button>
                    <Button onClick={handleDeleteAccount} color="error">
                        Delete Account
                    </Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
};

export default ProfilePage; 