// su dung CommonJS module syntax
// const express = require('express');

// Load bien moi truong tu file .env
import dotenv from 'dotenv';
dotenv.config();

// su dung ESM syntax
import express from 'express';
import connectDB from './config/database.js';

// import routes
import userRoutes from './routes/userRoutes.js';

// Tao ung dung Express
const app = express();

// connect to database: MongoDB
connectDB();

app.use("/api/users", userRoutes);

// Cau hinh cong lang nghe
// Su dung bien moi truong hoac cong mac dinh 5000, bien moi truong duoc dat trong file .env
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
    // In ra thong bao khi server bat dau chay
    console.log(`Server running on port ${PORT}`);
});

app.post("/api/tasks", (req, res) => {
    res.status(201).json({ message: "Task created" });
});