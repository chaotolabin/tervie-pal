# Auth Service - Business logic for authentication
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import uuid
import hashlib

from app.repositories import (
    UserRepository, RefreshTokenRepository, ProfileRepository,
    GoalRepository, BiometricsRepository
)
from app.api.deps import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    hash_refresh_token,
    decode_token,
)
from app.models.auth import User
from app.services.biometric_service import BiometricService



class AuthService:
    """Service layer for authentication operations"""
    
    @staticmethod
    def register(
        db: Session,
        username: str,
        email: str,
        password: str,
        **user_data
    ) -> tuple[User, str, str]:
        """
        Register new user with profile and initial goal
        
        Returns:
            (user, access_token, refresh_token)
        """
        # Check if user already exists
        if UserRepository.get_by_email(db, email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        if UserRepository.get_by_username(db, username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Extract profile and goal parameters
        full_name = user_data.get("full_name")
        gender = user_data.get("gender")
        date_of_birth = user_data.get("date_of_birth")
        height_cm = user_data.get("height_cm")
        weight_kg = user_data.get("weight_kg")
        baseline_activity = user_data.get("baseline_activity", "sedentary")
        goal_type = user_data.get("goal_type")
        weekly_goal = user_data.get("weekly_goal")
        goal_weight_kg = user_data.get("goal_weight_kg", weight_kg)
        weekly_exercise_min = user_data.get("weekly_exercise_min", 150)
        device_label = user_data.get("device_label", "Web Registration")
        user_agent = user_data.get("user_agent", "Unknown")
        ip_address = user_data.get("ip_address", "0.0.0.0")
        
        # Create user
        user = UserRepository.create(
            db,
            username=username,
            email=email,
            password_hash=hash_password(password),
        )
        db.add(user)
        db.flush()  # Generate user.id
        
        # Create profile
        ProfileRepository.create(
            db=db,
            user_id=user.id,
            full_name=full_name,
            gender=gender,
            date_of_birth=date_of_birth,
            height_cm_default=height_cm
        )
        
        # Calculate daily calorie target using GoalService
        from app.services.goal_service import GoalService
        
        # Tính BMR (Basal Metabolic Rate)
        bmr = GoalService.calculate_bmr(
            weight_kg=float(weight_kg),
            height_cm=float(height_cm),
            gender=gender,
            date_of_birth=date_of_birth
        )
        
        # Tính TDEE (Total Daily Energy Expenditure)
        tdee = GoalService.calculate_tdee(bmr=bmr, baseline_activity=baseline_activity)

        # Tính daily calorie target dựa trên TDEE
        daily_calorie = GoalService.calculate_daily_calorie(
            tdee=tdee,
            goal_type=goal_type,
            weekly_goal=weekly_goal
        )
        
        # Validate minimum calorie
        if daily_calorie < 1200:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Calculated daily calorie target is too low. Adjust goal parameters."
            )
        
        # Calculate macros
        macros = GoalService.calculate_macros(daily_calorie, goal_type, baseline_activity, float(weight_kg))
                
        # Create goal
        GoalRepository.create(
            db=db,
            user_id=user.id,
            goal_type=goal_type,
            target_weight_kg=goal_weight_kg,
            daily_calorie_target=daily_calorie,
            protein_grams=macros["protein_grams"],
            fat_grams=macros["fat_grams"],
            carb_grams=macros["carb_grams"],
            weekly_exercise_min=weekly_exercise_min
        )
        
        # Tính BMI trước
        bmi = BiometricService.calculate_bmi(weight_kg, height_cm)

        BiometricsRepository.create(
            db=db,
            user_id=user.id,
            weight_kg=weight_kg,
            height_cm=height_cm,
            bmi=bmi 
        )
        
        # Generate tokens
        access_token = create_access_token(user.id)
        refresh_token, refresh_token_hash = create_refresh_token(user.id)
        
        # Store refresh token session
        RefreshTokenRepository.create(
            db=db,
            user_id=user.id,
            token_hash=refresh_token_hash,
            device_label=device_label,
            user_agent=user_agent,
            ip=ip_address
        )
        
        # Commit all changes
        db.commit()
        db.refresh(user)
        
        return user, access_token, refresh_token
    
    @staticmethod
    def login(
        db: Session,
        email_or_username: str,
        password: str,
        device_label: str = None,
        user_agent: str = None,
        ip: str = None
    ) -> tuple[User, str, str]:
        """
        Login user and return user with tokens
        
        Returns:
            (user, access_token, refresh_token)
        """
        # Find user
        user = UserRepository.get_by_email_or_username(db, email_or_username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email/username or password"
            )
        
        # Verify password
        if not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email/username or password"
            )
        
        # Create tokens
        access_token = create_access_token(user.id)
        refresh_token, refresh_token_hash = create_refresh_token(user.id)
        
        # Store refresh token
        RefreshTokenRepository.create(
            db,
            user_id=user.id,
            token_hash=refresh_token_hash,
            device_label=device_label,
            user_agent=user_agent,
            ip=ip
        )
        
        db.commit()
        
        return user, access_token, refresh_token
    
    @staticmethod
    def refresh_access_token(
        db: Session,
        refresh_token: str
    ) -> tuple[str, str]:
        """
        Refresh access token using refresh token
        
        Returns:
            (new_access_token, new_refresh_token)
        """
        # Decode refresh token
        try:
            payload = decode_token(refresh_token)
            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )
        
        user_id_str = payload.get("sub")
        user_id = uuid.UUID(user_id_str)
        
        # Verify refresh token is stored and not revoked
        refresh_token_hash = hash_refresh_token(refresh_token)
        session = RefreshTokenRepository.get_by_token_hash(db, refresh_token_hash)
        
        if not session or session.revoked_at is not None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token invalid or revoked"
            )
        
        # Update last used
        RefreshTokenRepository.update_last_used(db, session)
        
        # Create new tokens
        new_access_token = create_access_token(user_id)
        new_refresh_token, new_refresh_token_hash = create_refresh_token(user_id)
        
        # Replace old refresh token with new one
        RefreshTokenRepository.revoke(db, session)
        RefreshTokenRepository.create(
            db,
            user_id=user_id,
            token_hash=new_refresh_token_hash
        )
        
        db.commit()
        
        return new_access_token, new_refresh_token
    
    @staticmethod
    def logout(db: Session, refresh_token: str) -> None:
        """Logout user - revoke refresh token"""
        refresh_token_hash = hash_refresh_token(refresh_token)
        session = RefreshTokenRepository.get_by_token_hash(db, refresh_token_hash)
        
        if session:
            RefreshTokenRepository.revoke(db, session)
            db.commit()
