const mongoose = require('mongoose');

const workoutLogSchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  date: {
    type: Date,
    required: true,
    default: Date.now
  },
  workoutName: {
    type: String,
    default: 'Workout Session'
  },
  sets: [{
    exerciseId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'Exercise',
      required: true
    },
    reps: {
      type: Number,
      min: 0
    },
    weight: {
      type: Number,
      min: 0
    },
    duration: {
      type: Number, // minutes
      required: true,
      min: 1
    },
    caloriesBurned: Number
  }],
  metrics: {
    totalVolume: { type: Number, default: 0 },
    totalDuration: { type: Number, default: 0 },
    totalCaloriesBurned: { type: Number, default: 0 }
  },
  notes: String
}, {
  timestamps: true
});

// Calculate metrics before saving
workoutLogSchema.pre('save', function(next) {
  this.metrics = {
    totalVolume: 0,
    totalDuration: 0,
    totalCaloriesBurned: 0
  };
  
  this.sets.forEach(set => {
    this.metrics.totalVolume += (set.reps || 0) * (set.weight || 0);
    this.metrics.totalDuration += set.duration || 0;
    this.metrics.totalCaloriesBurned += set.caloriesBurned || 0;
  });
  
  next();
});

// Index for efficient queries
workoutLogSchema.index({ userId: 1, date: -1 });

module.exports = mongoose.model('WorkoutLog', workoutLogSchema);
