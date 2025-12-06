const mongoose = require('mongoose');

const exerciseSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true,
    trim: true
  },
  targetMuscle: {
    type: String,
    required: true,
    enum: ['chest', 'back', 'shoulders', 'arms', 'legs', 'abs', 'cardio', 'full_body']
  },
  equipment: {
    type: String,
    required: true,
    enum: ['none', 'dumbbell', 'barbell', 'machine', 'cable', 'resistance_band', 'kettlebell']
  },
  type: {
    type: String,
    enum: ['cardio', 'strength', 'flexibility', 'balance'],
    required: true
  },
  instructions: [String],
  caloriesBurnedPerMinute: {
    type: Number,
    required: true
  },
  media: {
    imageUrl: String,
    videoUrl: String
  },
  difficulty: {
    type: String,
    enum: ['beginner', 'intermediate', 'advanced'],
    required: true
  },
  source: {
    provider: String,
    updatedAt: Date
  }
}, {
  timestamps: true
});

// Index for search
exerciseSchema.index({ name: 'text', targetMuscle: 1, difficulty: 1 });

module.exports = mongoose.model('Exercise', exerciseSchema);
