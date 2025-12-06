import mongoose from 'mongoose';

const userProfileSchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true,
    unique: true
  },
  dateOfBirth: {
    type: Date,
    required: true
  },
  gender: {
    type: String,
    enum: ['male', 'female', 'other'],
    required: true
  },
  height: {
    type: Number,
    required: true,
    min: 50,
    max: 300 // cm
  },
  weight: {
    type: Number,
    required: true,
    min: 20,
    max: 500 // kg
  },
  activityLevel: {
    type: String,
    enum: ['sedentary', 'light', 'moderate', 'active', 'very_active'],
    default: 'moderate'
  },
  goal: {
    type: String,
    enum: ['lose_weight', 'maintain', 'gain_weight', 'build_muscle'],
    default: 'maintain'
  },
  targetWeight: {
    type: Number,
    min: 20,
    max: 500
  },
  foodPreferences: {
    likes: [String],
    dislikes: [String],
    allergies: [String]
  },
  healthConditions: [String],
  targetCalories: Number,
  bmi: Number,
  bmr: Number,
  tdee: Number
}, {
  timestamps: true
});

// Calculate health metrics before saving
userProfileSchema.pre('save', function(next) {
  // Calculate BMI
  this.bmi = this.weight / Math.pow(this.height / 100, 2);
  
  // Calculate BMR using Mifflin-St Jeor Equation
  const age = Math.floor((Date.now() - this.dateOfBirth) / (365.25 * 24 * 60 * 60 * 1000));
  if (this.gender === 'male') {
    this.bmr = 10 * this.weight + 6.25 * this.height - 5 * age + 5;
  } else {
    this.bmr = 10 * this.weight + 6.25 * this.height - 5 * age - 161;
  }
  
  // Calculate TDEE
  const activityFactors = {
    sedentary: 1.2,
    light: 1.375,
    moderate: 1.55,
    active: 1.725,
    very_active: 1.9
  };
  this.tdee = this.bmr * activityFactors[this.activityLevel];
  
  // Calculate target calories based on goal
  const goalAdjustments = {
    lose_weight: -500,
    maintain: 0,
    gain_weight: 300,
    build_muscle: 500
  };
  this.targetCalories = this.tdee + goalAdjustments[this.goal];
  
  next();
});

export default mongoose.model('UserProfile', userProfileSchema);
