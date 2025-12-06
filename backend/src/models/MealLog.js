const mongoose = require('mongoose');

const mealLogSchema = new mongoose.Schema({
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
  mealType: {
    type: String,
    enum: ['breakfast', 'lunch', 'dinner', 'snack'],
    required: true
  },
  items: [{
    foodId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'Food',
      required: true
    },
    servingQty: {
      type: Number,
      required: true,
      min: 0.1
    },
    servingUnit: String,
    grams: Number,
    nutrientsSnapshot: {
      calories: Number,
      protein: Number,
      fat: Number,
      carbs: Number,
      fiber: Number
    }
  }],
  totals: {
    calories: { type: Number, default: 0 },
    protein: { type: Number, default: 0 },
    fat: { type: Number, default: 0 },
    carbs: { type: Number, default: 0 },
    fiber: { type: Number, default: 0 }
  },
  notes: String
}, {
  timestamps: true
});

// Calculate totals before saving
mealLogSchema.pre('save', function(next) {
  this.totals = {
    calories: 0,
    protein: 0,
    fat: 0,
    carbs: 0,
    fiber: 0
  };
  
  this.items.forEach(item => {
    if (item.nutrientsSnapshot) {
      this.totals.calories += item.nutrientsSnapshot.calories || 0;
      this.totals.protein += item.nutrientsSnapshot.protein || 0;
      this.totals.fat += item.nutrientsSnapshot.fat || 0;
      this.totals.carbs += item.nutrientsSnapshot.carbs || 0;
      this.totals.fiber += item.nutrientsSnapshot.fiber || 0;
    }
  });
  
  next();
});

// Index for efficient queries
mealLogSchema.index({ userId: 1, date: -1 });

module.exports = mongoose.model('MealLog', mealLogSchema);
