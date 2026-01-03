# Goal Service - Business logic for goals and macro calculations
import uuid
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Optional, Dict, Any

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert as pg_insert
from fastapi import HTTPException


class GoalService:
    """
    Service for goal and calorie/macro calculations.
    
    Calculation Flow:
    1. Get latest biometrics (weight_kg, height_cm) from biometrics_logs
    2. Get profile data (gender, date_of_birth, baseline_activity)
    3. Calculate BMR using Mifflin-St Jeor formula
    4. Calculate TDEE = BMR × activity_multiplier
    5. Calculate daily_calorie = TDEE ± adjustment (based on goal_type)
    6. Calculate macros from daily_calorie
    
    All formulas are FIXED and cannot be modified by users.
    """
    
    @staticmethod
    def calculate_bmr(weight_kg: float, height_cm: float, gender: str, date_of_birth: date) -> float:
        """
        Calculate Basal Metabolic Rate using Mifflin-St Jeor formula
        
        Formula:
        - Male: BMR = 10 × weight(kg) + 6.25 × height(cm) - 5 × age(years) + 5
        - Female: BMR = 10 × weight(kg) + 6.25 × height(cm) - 5 × age(years) - 161
        
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
        
        Multipliers:
        - sedentary: 1.2 (little/no exercise)
        - low_active: 1.375 (light exercise 1-3 days/week)
        - moderately_active: 1.55 (moderate exercise 3-5 days/week)
        - very_active: 1.725 (hard exercise 6-7 days/week)
        - extremely_active: 1.9 (very hard exercise, physical job)
        
        Args:
            bmr: Basal Metabolic Rate
            baseline_activity: Activity level
        
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
        
        return round(bmr * activity_multiplier, 2)
    
    @staticmethod
    def calculate_daily_calorie(
        tdee: float,
        goal_type: str,
        weekly_goal: float = 0.5
    ) -> float:
        """
        Calculate daily calorie target based on goal
        
        Adjustment:
        - 1kg fat ≈ 7700 kcal
        - weekly_goal kg/week → daily deficit/surplus
        
        Args:
            tdee: Total Daily Energy Expenditure
            goal_type: lose_weight, gain_weight, maintain_weight, build_muscle, improve_health
            weekly_goal: Target kg change per week (0.25 - 1.0)
        
        Returns:
            daily_calorie_target in kcal/day
        
        Raises:
            HTTPException 400: If calculated calorie < 1200 (unsafe)
        """
        # 1kg = ~7700 kcal, weekly_goal kg/week = (weekly_goal * 7700) / 7 kcal/day
        daily_adjustment = (weekly_goal * 7700) / 7  # ≈ 1100 kcal/day for 1kg/week
        
        goal_type_lower = str(goal_type).lower()
        if goal_type_lower == "lose_weight":
            daily_calorie = tdee - daily_adjustment
        elif goal_type_lower in ["gain_weight", "build_muscle"]:
            daily_calorie = tdee + daily_adjustment
        else:  # maintain_weight, improve_health
            daily_calorie = tdee
        
        # Safety check: minimum 1200 kcal
        if daily_calorie < 1200:
            raise HTTPException(
                status_code=400,
                detail=f"Calculated calorie target ({round(daily_calorie)}) is below safe minimum (1200 kcal). "
                       f"Try reducing weekly_goal or choosing a different activity level."
            )
        
        return round(daily_calorie, 2)
    
    @staticmethod
    def calculate_macros(
        daily_calorie: float,
        goal_type: str,
        baseline_activity: str,
        weight_kg: float
    ) -> Dict[str, Decimal]:
        """
        Calculate macro grams from daily calorie target with physiological floor anchoring, and based on goal type and activity level.
        
        Logic:
        1. Calculate initial macros based on ratios (protein%, fat%, carb%)
        2. Apply physiological floor (minimum g/kg body weight) for Protein and Fat
        3. Rebalance Carbs with remaining calories
        
        Ratios are optimized for:
        - Goal type: lose_weight, gain_weight, build_muscle, maintain_weight, improve_health
        - Activity level: sedentary, low_active, moderately_active, very_active, extremely_active
        
        Args:
            daily_calorie: Daily calorie target
            goal_type: User's fitness goal
            baseline_activity: User's activity level
            weight_kg: Body weight in kg (for floor calculation)
        
        Returns:
            {"protein_grams": X, "fat_grams": Y, "carb_grams": Z}
            
        Raises:
            HTTPException 400: If calories too low to meet physiological floors
        """
        # Map goal_type to standard categories
        goal_map = {
            "build_muscle": "build_muscle",
            "gain_weight": "gain_weight",
            "lose_weight": "lose_weight",
            "maintain_weight": "maintain",
            "improve_health": "maintain"
        }
        
        # Map activity to activity group
        activity_map = {
            "sedentary": "sedentary",
            "low_active": "light",
            "moderately_active": "moderate",
            "very_active": "athlete",
            "extremely_active": "athlete"
        }
        
        goal_category = goal_map.get(goal_type.lower(), "maintain")
        activity_group = activity_map.get(baseline_activity.lower(), "light")
        
        # Macro ratios: (protein%, fat%, carb%)
        # Average values from provided tables, normalized to sum 100%
        macro_ratios = {
            "sedentary": {
                "build_muscle": (0.225, 0.275, 0.500),  # 22.5%, 27.5%, 50% → sum=100%
                "gain_weight": (0.175, 0.275, 0.550),   # 17.5%, 27.5%, 55% → sum=100%
                "lose_weight": (0.290, 0.237, 0.473),   # 29%, 23.7%, 47.3% → normalized from 27.5/22.5/45
                "maintain": (0.185, 0.289, 0.526)       # 18.5%, 28.9%, 52.6% → normalized from 17.5/27.5/50
            },
            "light": {
                "build_muscle": (0.258, 0.232, 0.510),  # 25.8%, 23.2%, 51% → normalized from 25/22.5/50
                "gain_weight": (0.200, 0.275, 0.525),   # 20%, 27.5%, 52.5% → sum=100%
                "lose_weight": (0.324, 0.243, 0.433),   # 32.4%, 24.3%, 43.3% → normalized from 30/22.5/40
                "maintain": (0.211, 0.289, 0.500)       # 21.1%, 28.9%, 50% → normalized from 20/27.5/50
            },
            "moderate": {
                "build_muscle": (0.275, 0.225, 0.500),  # 27.5%, 22.5%, 50% → sum=100%
                "gain_weight": (0.220, 0.268, 0.512),   # 22%, 26.8%, 51.2% → normalized from 22.5/27.5/52.5
                "lose_weight": (0.351, 0.216, 0.433),   # 35.1%, 21.6%, 43.3% → normalized from 32.5/20/40
                "maintain": (0.225, 0.275, 0.500)       # 22.5%, 27.5%, 50% → sum=100%
            },
            "athlete": {
                "build_muscle": (0.265, 0.217, 0.518),  # 26.5%, 21.7%, 51.8% → normalized from 27.5/22.5/52.5
                "gain_weight": (0.220, 0.268, 0.512),   # 22%, 26.8%, 51.2% → normalized from 22.5/27.5/55
                "lose_weight": (0.349, 0.199, 0.452),   # 34.9%, 19.9%, 45.2% → normalized from 32.5/18.5/40
                "maintain": (0.221, 0.233, 0.546)       # 22.1%, 23.3%, 54.6% → normalized from 22.5/23.75/55
            }
        }
        
        # Physiological floors (g/kg body weight)
        physiological_floors = {
            "lose_weight": {"protein": 1.8, "fat": 0.5},
            "build_muscle": {"protein": 1.6, "fat": 0.6},
            "gain_weight": {"protein": 1.2, "fat": 0.8},
            "maintain": {"protein": 1.0, "fat": 0.6}
        }
        
        # Step 1: Calculate initial macros based on ratios
        ratios = macro_ratios.get(activity_group, {}).get(goal_category, (0.20, 0.30, 0.50))
        protein_ratio, fat_ratio, carb_ratio = ratios  # khong dung carb_ratio directly
        
        initial_protein_grams = float(daily_calorie) * protein_ratio / 4
        initial_fat_grams = float(daily_calorie) * fat_ratio / 9
        
        # Step 2: Apply physiological floors
        floors = physiological_floors.get(goal_category, {"protein": 1.0, "fat": 0.6})
        min_protein_grams = weight_kg * floors["protein"]
        min_fat_grams = weight_kg * floors["fat"]
        
        # Take the maximum of calculated and floor values
        final_protein_grams = max(initial_protein_grams, min_protein_grams)
        final_fat_grams = max(initial_fat_grams, min_fat_grams)
        
        # Step 3: Calculate calories used by protein and fat
        protein_calories = final_protein_grams * 4
        fat_calories = final_fat_grams * 9
        used_calories = protein_calories + fat_calories
        
        # Step 4: Rebalance carbs with remaining calories
        remaining_calories = daily_calorie - used_calories
        
        if remaining_calories < 0:
            raise HTTPException(
                status_code=400,
                detail=f"Calorie target ({round(daily_calorie)} kcal) is too low to meet physiological requirements. "
                       f"Minimum needed: {round(used_calories)} kcal for protein ({round(final_protein_grams)}g) and fat ({round(final_fat_grams)}g). "
                       f"Please increase daily calorie target or adjust your goal."
            )
        
        final_carb_grams = max(0, remaining_calories / 4)
        
        return {
            "protein_grams": Decimal(str(round(final_protein_grams, 2))),
            "fat_grams": Decimal(str(round(final_fat_grams, 2))),
            "carb_grams": Decimal(str(round(final_carb_grams, 2)))
        }

    @staticmethod
    def get_latest_biometrics(db: Session, user_id: uuid.UUID):
        """
        Get the latest biometrics log for user
        
        Returns:
            BiometricsLog or None
        """
        from app.models.biometric import BiometricsLog
        from sqlalchemy import desc
        
        query = (
            select(BiometricsLog)
            .where(BiometricsLog.user_id == user_id)
            .order_by(desc(BiometricsLog.logged_at))
            .limit(1)
        )
        result = db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    def get_user_profile(db: Session, user_id: uuid.UUID):
        """
        Get user profile with required fields for calculation
        
        Returns:
            Profile or None
        """
        from app.models.auth import Profile
        
        query = select(Profile).where(Profile.user_id == user_id)
        result = db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    def get_goal(db: Session, user_id: uuid.UUID):
        """
        Get current goal for user
        
        Returns:
            Goal or None
        """
        from app.models.auth import Goal
        
        query = select(Goal).where(Goal.user_id == user_id)
        result = db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    def recalculate_goal(
        db: Session,
        user_id: uuid.UUID,
        goal_type: Optional[str] = None,
        baseline_activity: Optional[str] = None,
        weekly_goal: Optional[float] = None,
        target_weight_kg: Optional[float] = None,
        weekly_exercise_min: Optional[int] = None,
        commit: bool = True
    ) -> Dict[str, Any]:
        """
        Recalculate and upsert goal based on latest biometrics and profile.
        
        This is the MAIN method to call whenever:
        1. User creates/updates goal (PUT/PATCH /goals)
        2. User updates biometrics (POST/PATCH /biometrics)
        3. User updates profile (height, weight changes)
        
        Flow:
        1. Get latest biometrics → weight_kg, height_cm
        2. Get profile → gender, date_of_birth, baseline_activity (if not provided)
        3. Get existing goal → use existing values for None params
        4. Calculate BMR → TDEE → daily_calorie → macros
        5. Upsert Goal record
        
        Args:
            db: Database session
            user_id: User UUID
            goal_type: Optional new goal type
            baseline_activity: Optional new activity level
            weekly_goal: Optional new weekly goal (kg/week)
            target_weight_kg: Optional target weight
            weekly_exercise_min: Optional exercise minutes per week
            commit: Whether to commit the transaction (default True)
        
        Returns:
            Dict with calculated values and Goal object
        
        Raises:
            HTTPException 400: If missing required data (biometrics, profile)
        """
        from app.models.auth import Goal
        
        # Step 1: Get latest biometrics
        latest_biometrics = GoalService.get_latest_biometrics(db, user_id)
        if not latest_biometrics:
            raise HTTPException(
                status_code=400,
                detail="No biometrics data found. Please create a biometrics log first."
            )
        
        weight_kg = float(latest_biometrics.weight_kg)
        height_cm = float(latest_biometrics.height_cm)
        
        # Step 2: Get profile
        profile = GoalService.get_user_profile(db, user_id)
        if not profile:
            raise HTTPException(
                status_code=400,
                detail="Profile not found. Please complete your profile first."
            )
        
        if not profile.gender or not profile.date_of_birth:
            raise HTTPException(
                status_code=400,
                detail="Profile is incomplete. Please set gender and date_of_birth."
            )
        
        gender = profile.gender
        date_of_birth = profile.date_of_birth
        
        # Step 3: Get existing goal for default values
        existing_goal = GoalService.get_goal(db, user_id)
        
        # Resolve final values (priority: param > existing > default)
        final_goal_type = goal_type or (existing_goal.goal_type if existing_goal else None)
        if not final_goal_type:
            raise HTTPException(
                status_code=400,
                detail="goal_type is required when creating a new goal."
            )
        
        # baseline_activity: param > existing > default
        final_baseline_activity = baseline_activity or (
            existing_goal.baseline_activity if existing_goal and existing_goal.baseline_activity else "low_active"
        )
        
        # weekly_goal: param > existing > default
        if weekly_goal is not None:
            final_weekly_goal = weekly_goal
        elif existing_goal and existing_goal.weekly_goal is not None:
            final_weekly_goal = float(existing_goal.weekly_goal)
        else:
            final_weekly_goal = 0.5
        
        final_target_weight_kg = target_weight_kg or (
            float(existing_goal.target_weight_kg) if existing_goal and existing_goal.target_weight_kg else None
        )
        final_weekly_exercise_min = weekly_exercise_min if weekly_exercise_min is not None else (
            existing_goal.weekly_exercise_min if existing_goal else None
        )
        
        # Step 4: Calculate BMR → TDEE → daily_calorie → macros
        bmr = GoalService.calculate_bmr(weight_kg, height_cm, gender, date_of_birth)
        tdee = GoalService.calculate_tdee(bmr, final_baseline_activity)
        daily_calorie = GoalService.calculate_daily_calorie(
            tdee, final_goal_type, final_weekly_goal
        )
        macros = GoalService.calculate_macros(daily_calorie, final_goal_type, final_baseline_activity, weight_kg)
        
        # Step 5: Upsert Goal using PostgreSQL INSERT ... ON CONFLICT
        stmt = pg_insert(Goal).values(
            user_id=user_id,
            goal_type=final_goal_type,
            baseline_activity=final_baseline_activity,
            weekly_goal=final_weekly_goal,
            target_weight_kg=Decimal(str(final_target_weight_kg)) if final_target_weight_kg else None,
            daily_calorie_target=Decimal(str(daily_calorie)),
            protein_grams=macros["protein_grams"],
            fat_grams=macros["fat_grams"],
            carb_grams=macros["carb_grams"],
            weekly_exercise_min=final_weekly_exercise_min
        )
        
        stmt = stmt.on_conflict_do_update(
            index_elements=[Goal.user_id],
            set_={
                "goal_type": stmt.excluded.goal_type,
                "baseline_activity": stmt.excluded.baseline_activity,
                "weekly_goal": stmt.excluded.weekly_goal,
                "target_weight_kg": stmt.excluded.target_weight_kg,
                "daily_calorie_target": stmt.excluded.daily_calorie_target,
                "protein_grams": stmt.excluded.protein_grams,
                "fat_grams": stmt.excluded.fat_grams,
                "carb_grams": stmt.excluded.carb_grams,
                "weekly_exercise_min": stmt.excluded.weekly_exercise_min,
                "updated_at": datetime.now(timezone.utc)
            }
        )
        
        db.execute(stmt)
        
        if commit:
            db.commit()
        
        # Fetch updated goal
        updated_goal = GoalService.get_goal(db, user_id)
        
        return {
            "goal": updated_goal,
            "calculated": {
                "weight_kg": weight_kg,
                "height_cm": height_cm,
                "gender": gender,
                "age_years": int((date.today() - date_of_birth).days / 365.25),
                "bmr": bmr,
                "tdee": tdee,
                "daily_calorie_target": daily_calorie,
                "protein_grams": float(macros["protein_grams"]),
                "fat_grams": float(macros["fat_grams"]),
                "carb_grams": float(macros["carb_grams"]),
            }
        }

    @staticmethod
    def calculate_preview(
        db: Session,
        user_id: uuid.UUID,
        goal_type: str,
        baseline_activity: str,
        weekly_goal: float = 0.5
    ) -> Dict[str, Any]:
        """
        Calculate goal preview WITHOUT saving to database.
        Use for POST /goals/calculate endpoint.
        
        Args:
            db: Database session
            user_id: User UUID
            goal_type: Goal type
            baseline_activity: Activity level
            weekly_goal: Weekly goal in kg
        
        Returns:
            Dict with all calculated values
        """
        # Get latest biometrics
        latest_biometrics = GoalService.get_latest_biometrics(db, user_id)
        if not latest_biometrics:
            raise HTTPException(
                status_code=400,
                detail="No biometrics data found. Please create a biometrics log first."
            )
        
        weight_kg = float(latest_biometrics.weight_kg)
        height_cm = float(latest_biometrics.height_cm)
        
        # Get profile
        profile = GoalService.get_user_profile(db, user_id)
        if not profile or not profile.gender or not profile.date_of_birth:
            raise HTTPException(
                status_code=400,
                detail="Profile is incomplete. Please set gender and date_of_birth."
            )
        
        gender = profile.gender
        date_of_birth = profile.date_of_birth
        age_years = int((date.today() - date_of_birth).days / 365.25)
        
        # Calculate
        bmr = GoalService.calculate_bmr(weight_kg, height_cm, gender, date_of_birth)
        tdee = GoalService.calculate_tdee(bmr, baseline_activity)
        daily_calorie = GoalService.calculate_daily_calorie(tdee, goal_type, weekly_goal)
        macros = GoalService.calculate_macros(daily_calorie, goal_type, baseline_activity, weight_kg)
        
        return {
            "goal_type": goal_type,
            "baseline_activity": baseline_activity,
            "weekly_goal": weekly_goal,
            "weight_kg": weight_kg,
            "height_cm": height_cm,
            "gender": gender,
            "age_years": age_years,
            "bmr": bmr,
            "tdee": tdee,
            "daily_calorie_target": daily_calorie,
            "protein_grams": float(macros["protein_grams"]),
            "fat_grams": float(macros["fat_grams"]),
            "carb_grams": float(macros["carb_grams"]),
        }

    @staticmethod
    def update_weekly_exercise_min(
        db: Session,
        user_id: uuid.UUID,
        weekly_exercise_min: int
    ):
        """
        Update only weekly_exercise_min without recalculating other values.
        This is a lightweight update for just changing exercise goal.
        """
        from app.models.auth import Goal
        
        goal = GoalService.get_goal(db, user_id)
        if not goal:
            raise HTTPException(
                status_code=404,
                detail="Goal not found. Please create a goal first."
            )
        
        goal.weekly_exercise_min = weekly_exercise_min
        db.commit()
        db.refresh(goal)
        
        return goal

