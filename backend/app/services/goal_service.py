# Goal Service - Business logic for goals and macro calculations
from datetime import date
from decimal import Decimal


class GoalService:
    """Service for goal and calorie/macro calculations"""
    
    @staticmethod
    def calculate_bmr(weight_kg: float, height_cm: float, gender: str, date_of_birth: date) -> float:
        """
        Calculate Basal Metabolic Rate using Mifflin-St Jeor formula
        
        Args:
            weight_kg: Weight in kg
            height_cm: Height in cm
            gender: 'male' or 'female'
            date_of_birth: Date of birth
        
        Returns:
            BMR in kcal/day
        """
        from datetime import date as date_class
        
        today = date_class.today()
        age_years = (today - date_of_birth).days / 365.25
        
        if str(gender).lower() == "male":
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age_years + 5
        else:
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age_years - 161
        
        return bmr
    
    @staticmethod
    def calculate_tdee(bmr: float, baseline_activity: str) -> float:
        """
        Calculate Total Daily Energy Expenditure
        
        Args:
            bmr: Basal Metabolic Rate
            baseline_activity: Activity level (sedentary, low_active, moderately_active, very_active, extremely_active)
        
        Returns:
            TDEE in kcal/day
        """
        activity_multipliers = {
            "sedentary": 1.2,
            "low_active": 1.375,
            "moderately_active": 1.55,
            "very_active": 1.725,
            "extremely_active": 1.9,
        }
        
        baseline_activity_lower = str(baseline_activity).lower()
        activity_multiplier = activity_multipliers.get(baseline_activity_lower, 1.375)
        
        return bmr * activity_multiplier
    
    @staticmethod
    def calculate_daily_calorie(
        weight_kg: float,
        height_cm: float,
        gender: str,
        date_of_birth: date,
        baseline_activity: str,
        goal_type: str,
        weekly_goal: float
    ) -> float:
        """
        Calculate daily calorie target based on goal
        
        Returns:
            daily_calorie_target in kcal/day
        """
        # Calculate BMR and TDEE
        bmr = GoalService.calculate_bmr(weight_kg, height_cm, gender, date_of_birth)
        tdee = GoalService.calculate_tdee(bmr, baseline_activity)
        
        # Apply calorie adjustment for goal
        calorie_adjustment = weekly_goal * 1000  # Approximate: 1kg ≈ 7700 kcal
        
        goal_type_lower = str(goal_type).lower()
        if goal_type_lower == "lose_weight":
            daily_calorie = tdee - calorie_adjustment
        elif goal_type_lower == "gain_weight":
            daily_calorie = tdee + calorie_adjustment
        elif goal_type_lower == "build_muscle":
            daily_calorie = tdee + calorie_adjustment
        else:  # maintain_weight, improve_health
            daily_calorie = tdee
        
        # Validate minimum calorie
        if daily_calorie < 1200:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=400,
                detail=f"Calorie target too low (min 1200, got {round(daily_calorie, 2)})"
            )
        
        return daily_calorie
    
    @staticmethod
    def calculate_macros(daily_calorie: float) -> dict:
        """
        Calculate macro grams from daily calorie target
        
        Ratios:
        - Protein: 20% (4 kcal/g)
        - Fat: 30% (9 kcal/g)
        - Carbs: 50% (4 kcal/g)
        
        Returns:
            {"protein_grams": X, "fat_grams": Y, "carb_grams": Z}
        """
        protein_grams = float(daily_calorie) * 0.20 / 4
        fat_grams = float(daily_calorie) * 0.30 / 9
        carb_grams = float(daily_calorie) * 0.50 / 4
        
        return {
            "protein_grams": Decimal(str(round(protein_grams, 2))),
            "fat_grams": Decimal(str(round(fat_grams, 2))),
            "carb_grams": Decimal(str(round(carb_grams, 2)))
        }
