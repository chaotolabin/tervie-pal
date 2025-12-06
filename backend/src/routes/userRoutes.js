import express from 'express';
import { getProfile } from '../controllers/userController.js';

const router = express.Router();

// userController la cac ham xu ly logic cho nguoi dung
// const userController = require('../controllers/userController.js');

router.get('/profile', getProfile);

export default router;  // Export the router to be used in other parts of the application