const mongoose = require('mongoose');

const foodSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true,
    trim: true
  },
  nutrients: {
    calories: { type: Number, required: true },
    protein: { type: Number, required: true },
    fat: { type: Number, required: true },
    carbs: { type: Number, required: true },
    fiber: { type: Number, default: 0 },
    sugar: { type: Number, default: 0 },
    sodium: { type: Number, default: 0 },
    vitamins: {
      vitaminA: { type: Number, default: 0 },
      vitaminC: { type: Number, default: 0 },
      vitaminD: { type: Number, default: 0 }
    }
  },
  serving: {
    qty: { type: Number, required: true },
    unit: { type: String, required: true },
    grams: { type: Number, required: true }
  },
  tags: [String],
  category: {
    type: String,
    enum: ['protein', 'carbs', 'vegetables', 'fruits', 'dairy', 'fats', 'snacks', 'beverages'],
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
foodSchema.index({ name: 'text', tags: 'text' });

module.exports = mongoose.model('Food', foodSchema);
