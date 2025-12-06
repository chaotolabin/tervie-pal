import UserProfile from '../models/UserProfile.js';

// Get user profile
export const getProfile = async (req, res) => {
    try {
        const profile = await UserProfile.findOne({ userId: req.userId });
        
        if (!profile) {
        return res.status(404).json({ message: 'Profile not found' });
        }

        res.json(profile);
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};