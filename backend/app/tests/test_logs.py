"""
Unit Tests cho Daily Logs Service
Test business logic: Tính toán dinh dưỡng, aggregation, CRUD operations
"""
import pytest
import uuid
from datetime import datetime, timezone, date
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi import HTTPException

from app.models.base import Base
from app.models.auth import User
from app.models.food import Food, FoodNutrient, FoodPortion
from app.models.exercise import Exercise
from app.models.biometric import BiometricsLog
from app.models.log import (
    FoodLogEntry, FoodLogItem,
    ExerciseLogEntry, ExerciseLogItem,
    MealType
)
from app.schemas.log_schema import (
    FoodLogEntryCreate,
    FoodLogEntryPatch,
    FoodLogItemCreate,
    FoodLogItemUpdate,
    ExerciseLogEntryCreate,
    ExerciseLogEntryPatch,
    ExerciseLogItemCreate,
    ExerciseLogItemUpdate
)
from app.services.logs import (
    FoodLogService,
    ExerciseLogService,
    DailyLogService
)


# ==================== FIXTURES ====================

@pytest.fixture(scope="function")
def db_session():
    """Tạo in-memory SQLite database cho testing"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    yield session
    
    session.close()


@pytest.fixture
def test_user(db_session: Session):
    """Tạo test user"""
    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        full_name="Test User"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_food(db_session: Session):
    """Tạo test food với nutrients"""
    food = Food(
        id=1,
        owner_user_id=None,  # Global food
        name="Bánh mỳ",
        food_group="Grains"
    )
    db_session.add(food)
    db_session.flush()
    
    # Thêm nutrients
    nutrients = [
        FoodNutrient(
            food_id=food.id,
            nutrient_name="calories",
            unit="kcal",
            amount_per_100g=Decimal("265.0")
        ),
        FoodNutrient(
            food_id=food.id,
            nutrient_name="protein",
            unit="g",
            amount_per_100g=Decimal("9.0")
        ),
        FoodNutrient(
            food_id=food.id,
            nutrient_name="carbs",
            unit="g",
            amount_per_100g=Decimal("49.0")
        ),
        FoodNutrient(
            food_id=food.id,
            nutrient_name="fat",
            unit="g",
            amount_per_100g=Decimal("3.2")
        )
    ]
    
    for nutrient in nutrients:
        db_session.add(nutrient)
    
    db_session.commit()
    db_session.refresh(food)
    return food


@pytest.fixture
def test_exercise(db_session: Session):
    """Tạo test exercise"""
    exercise = Exercise(
        id=1,
        owner_user_id=None,  # Global exercise
        activity_code="RUN001",
        major_heading="Running",
        description="Running, moderate pace",
        met_value=Decimal("8.0")
    )
    db_session.add(exercise)
    db_session.commit()
    db_session.refresh(exercise)
    return exercise


@pytest.fixture
def test_biometric(db_session: Session, test_user):
    """Tạo test biometric log"""
    biometric = BiometricsLog(
        user_id=test_user.id,
        logged_at=datetime.now(timezone.utc),
        weight_kg=Decimal("70.0"),
        height_cm=Decimal("170.0"),
        bmi=Decimal("24.2")
    )
    db_session.add(biometric)
    db_session.commit()
    db_session.refresh(biometric)
    return biometric


# ==================== FOOD LOG TESTS ====================

class TestFoodLogService:
    """Test cases cho FoodLogService"""

    @pytest.fixture
    def test_food_with_portions(db_session: Session):
        """Tạo test food với portions"""
        food = Food(
            id=1,
            name="Bánh mỳ",
            food_group="Grains"
        )
        db_session.add(food)
        db_session.flush()
        
        # Thêm nutrients (giữ nguyên như cũ)
        nutrients = [...]
        for nutrient in nutrients:
            db_session.add(nutrient)
        
        # THÊM: Portions
        portions = [
            FoodPortion(
                food_id=food.id,
                amount=Decimal("1"),
                unit="slice",
                grams=Decimal("50")  # 1 slice = 50g
            ),
            FoodPortion(
                food_id=food.id,
                amount=Decimal("1"),
                unit="cup",
                grams=Decimal("158")  # 1 cup = 158g
            )
        ]
        for portion in portions:
            db_session.add(portion)
        
        db_session.commit()
        db_session.refresh(food)
        return food, portions

    def test_create_food_log_success(self, db_session, test_user, test_food_with_portions):
        """Test tạo food log thành công"""
        test_food, portions = test_food_with_portions
        slice_portion = portions[0]  # portion_id tương ứng với slice
        # Arrange
        data = FoodLogEntryCreate(
            logged_at=datetime.now(timezone.utc),
            meal_type=MealType.BREAKFAST,
            items=[
                FoodLogItemCreate(
                    food_id=test_food.id,
                    portion_id=slice_portion.id,
                    quantity=Decimal("2")
                    # unit="slice",
                    # grams=Decimal("100")  # 100g
                )
            ]
        )
        
        # Act
        entry = FoodLogService.create_food_log(db_session, test_user.id, data)
        
        # Assert
        assert entry is not None
        assert entry.user_id == test_user.id
        assert entry.meal_type == MealType.BREAKFAST
        assert len(entry.items) == 1
        
        # Kiểm tra tính toán dinh dưỡng
        # 100g bánh mỳ = 265 kcal (từ fixture)
        item = entry.items[0]
        assert item.portion_id == slice_portion.id
        assert item.quantity == Decimal("2")
        assert item.unit == "slice"  # Server tự set
        assert item.grams == Decimal("100")  # 2 × 50g = 100g
        
        assert item.calories == Decimal("265.00")
        assert item.protein_g == Decimal("9.000")
        assert item.carbs_g == Decimal("49.000")
        assert item.fat_g == Decimal("3.200")
        
        # Kiểm tra tổng
        assert entry.total_calories == Decimal("265.00")
        assert entry.total_protein_g == Decimal("9.000")

    def test_create_food_log_multiple_items(self, db_session, test_user, test_food):
        """Test tạo food log với nhiều món"""
        # Arrange
        data = FoodLogEntryCreate(
            logged_at=datetime.now(timezone.utc),
            meal_type=MealType.LUNCH,
            items=[
                FoodLogItemCreate(
                    food_id=test_food.id,
                    quantity=Decimal("1"),
                    unit="serving",
                    grams=Decimal("100")
                ),
                FoodLogItemCreate(
                    food_id=test_food.id,
                    quantity=Decimal("2"),
                    unit="slice",
                    grams=Decimal("200")  # 200g
                )
            ]
        )
        
        # Act
        entry = FoodLogService.create_food_log(db_session, test_user.id, data)
        
        # Assert
        assert len(entry.items) == 2
        
        # 100g + 200g = 300g bánh mỳ = 795 kcal (265 * 3)
        expected_calories = Decimal("265") * Decimal("3")
        assert entry.total_calories == round(expected_calories, 2)

    def test_create_food_log_invalid_food_id(self, db_session, test_user):
        """Test tạo food log với food_id không tồn tại"""
        # Arrange
        data = FoodLogEntryCreate(
            logged_at=datetime.now(timezone.utc),
            meal_type=MealType.DINNER,
            items=[
                FoodLogItemCreate(
                    food_id=9999,  # Không tồn tại
                    quantity=Decimal("1"),
                    unit="serving",
                    grams=Decimal("100")
                )
            ]
        )
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            FoodLogService.create_food_log(db_session, test_user.id, data)
        
        assert exc_info.value.status_code == 400
        assert "not found" in str(exc_info.value.detail).lower()

    def test_create_food_log_invalid_portion(self, db_session, test_user, test_food_with_portions):
        """Test lỗi khi portion_id không thuộc food"""
        food, portions = test_food_with_portions
        
        # Arrange - Gửi portion_id của food khác
        data = FoodLogEntryCreate(
            logged_at=datetime.now(timezone.utc),
            meal_type=MealType.BREAKFAST,
            items=[
                FoodLogItemCreate(
                    food_id=food.id,
                    portion_id=9999,  # Không tồn tại hoặc không thuộc food này
                    quantity=Decimal("1")
                )
            ]
        )
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            FoodLogService.create_food_log(db_session, test_user.id, data)
        
        assert exc_info.value.status_code == 400
        assert "portion" in str(exc_info.value.detail).lower()

    def test_get_daily_food_logs(self, db_session, test_user, test_food):
        """Test lấy food logs trong ngày"""
        # Arrange - Tạo 2 entries trong cùng 1 ngày
        today = datetime.now(timezone.utc)
        
        for meal in [MealType.BREAKFAST, MealType.LUNCH]:
            data = FoodLogEntryCreate(
                logged_at=today,
                meal_type=meal,
                items=[
                    FoodLogItemCreate(
                        food_id=test_food.id,
                        quantity=Decimal("1"),
                        unit="serving",
                        grams=Decimal("100")
                    )
                ]
            )
            FoodLogService.create_food_log(db_session, test_user.id, data)
        
        # Act
        entries = FoodLogService.get_daily_food_logs(
            db_session,
            test_user.id,
            today.date()
        )
        
        # Assert
        assert len(entries) == 2
        assert entries[0].meal_type == MealType.BREAKFAST
        assert entries[1].meal_type == MealType.LUNCH

    def test_delete_food_log(self, db_session, test_user, test_food):
        """Test xóa food log"""
        # Arrange
        data = FoodLogEntryCreate(
            logged_at=datetime.now(timezone.utc),
            meal_type=MealType.SNACKS,
            items=[
                FoodLogItemCreate(
                    food_id=test_food.id,
                    quantity=Decimal("1"),
                    unit="serving",
                    grams=Decimal("50")
                )
            ]
        )
        entry = FoodLogService.create_food_log(db_session, test_user.id, data)
        
        # Act
        FoodLogService.delete_food_log(db_session, entry.id, test_user.id)
        
        # Assert
        db_session.refresh(entry)
        assert entry.deleted_at is not None

    def test_update_food_log(self, db_session, test_user, test_food):
        """Test cập nhật food log"""
        # Arrange
        original_time = datetime.now(timezone.utc)
        data = FoodLogEntryCreate(
            logged_at=original_time,
            meal_type=MealType.BREAKFAST,
            items=[
                FoodLogItemCreate(
                    food_id=test_food.id,
                    quantity=Decimal("1"),
                    unit="serving",
                    grams=Decimal("100")
                )
            ]
        )
        entry = FoodLogService.create_food_log(db_session, test_user.id, data)
        
        # Act - Update meal_type
        update_data = FoodLogEntryPatch(meal_type=MealType.LUNCH)
        updated_entry = FoodLogService.update_food_log(
            db_session, 
            entry.id, 
            test_user.id, 
            update_data
        )
        
        # Assert
        assert updated_entry.meal_type == MealType.LUNCH
        assert updated_entry.logged_at == original_time  # Không đổi
        # Items và nutrients không đổi
        assert updated_entry.total_calories == entry.total_calories

    def test_update_food_log_partial(self, db_session, test_user, test_food):
        """Test partial update (chỉ update logged_at)"""
        # Arrange
        original_time = datetime.now(timezone.utc)
        data = FoodLogEntryCreate(
            logged_at=original_time,
            meal_type=MealType.DINNER,
            items=[
                FoodLogItemCreate(
                    food_id=test_food.id,
                    quantity=Decimal("1"),
                    unit="serving",
                    grams=Decimal("100")
                )
            ]
        )
        entry = FoodLogService.create_food_log(db_session, test_user.id, data)
        
        # Act - Chỉ update logged_at
        from datetime import timedelta
        new_time = original_time + timedelta(hours=2)
        update_data = FoodLogEntryPatch(logged_at=new_time)
        updated_entry = FoodLogService.update_food_log(
            db_session,
            entry.id,
            test_user.id,
            update_data
        )
        
        # Assert
        assert updated_entry.logged_at == new_time
        assert updated_entry.meal_type == MealType.DINNER  # Không đổi

    def test_update_food_log_item(self, db_session, test_user, test_food):
        """Test cập nhật món ăn với ratio-based calculation"""
        # Arrange - Tạo entry với 100g bánh mỳ = 265 kcal
        data = FoodLogEntryCreate(
            logged_at=datetime.now(timezone.utc),
            meal_type=MealType.BREAKFAST,
            items=[
                FoodLogItemCreate(
                    food_id=test_food.id,
                    quantity=Decimal("1"),
                    unit="serving",
                    grams=Decimal("100")  # 100g = 265 kcal
                )
            ]
        )
        entry = FoodLogService.create_food_log(db_session, test_user.id, data)
        item_id = entry.items[0].id
        original_calories = entry.items[0].calories
        
        # Act - Tăng gấp đôi grams (100g -> 200g)
        update_data = FoodLogItemUpdate(grams=Decimal("200"))
        updated_item = FoodLogService.update_food_log_item(
            db_session,
            item_id,
            test_user.id,
            update_data
        )
        
        # Assert - Calories cũng phải gấp đôi
        assert updated_item.grams == Decimal("200")
        assert updated_item.calories == original_calories * Decimal("2")
        
        # Kiểm tra entry đã được re-aggregate
        db_session.refresh(entry)
        assert entry.total_calories == original_calories * Decimal("2")

    def test_update_food_log_item_zero_grams_error(self, db_session, test_user, test_food):
        """Test error khi update item có grams = 0"""
        # Arrange - Tạo item với grams = 0 (edge case)
        entry = FoodLogEntry(
            user_id=test_user.id,
            logged_at=datetime.now(timezone.utc),
            meal_type=MealType.LUNCH,
            total_calories=Decimal(0)
        )
        db_session.add(entry)
        db_session.flush()
        
        item = FoodLogItem(
            entry_id=entry.id,
            food_id=test_food.id,
            quantity=Decimal("1"),
            unit="serving",
            grams=Decimal("0"),  # Edge case
            calories=Decimal("100")
        )
        db_session.add(item)
        db_session.commit()
        
        # Act & Assert
        update_data = FoodLogItemUpdate(grams=Decimal("100"))
        with pytest.raises(HTTPException) as exc_info:
            FoodLogService.update_food_log_item(
                db_session,
                item.id,
                test_user.id,
                update_data
            )
        
        assert exc_info.value.status_code == 400
        assert "0 grams" in str(exc_info.value.detail).lower()


# ==================== EXERCISE LOG TESTS ======================================

class TestExerciseLogService:
    """Test cases cho ExerciseLogService"""

    def test_create_exercise_log_success(
        self, 
        db_session, 
        test_user, 
        test_exercise, 
        test_biometric
    ):
        """Test tạo exercise log thành công"""
        # Arrange
        data = ExerciseLogEntryCreate(
            logged_at=datetime.now(timezone.utc),
            items=[
                ExerciseLogItemCreate(
                    exercise_id=test_exercise.id,
                    duration_min=Decimal("30"),  # 30 phút
                    notes="Morning run"
                )
            ]
        )
        
        # Act
        entry = ExerciseLogService.create_exercise_log(db_session, test_user.id, data)
        
        # Assert
        assert entry is not None
        assert entry.user_id == test_user.id
        assert len(entry.items) == 1
        
        # Kiểm tra tính toán calories
        # Formula: Calories = MET × weight(kg) × duration(hours)
        # = 8.0 × 70 × 0.5 = 280 kcal
        item = entry.items[0]
        expected_calories = Decimal("8.0") * Decimal("70") * (Decimal("30") / Decimal("60"))
        assert item.calories == round(expected_calories, 2)
        assert item.met_value_snapshot == test_exercise.met_value
        
        # Kiểm tra tổng
        assert entry.total_calories == round(expected_calories, 2)

    def test_create_exercise_log_no_biometric(self, db_session, test_user, test_exercise):
        """Test tạo exercise log khi user chưa có biometric log"""
        # Arrange
        data = ExerciseLogEntryCreate(
            logged_at=datetime.now(timezone.utc),
            items=[
                ExerciseLogItemCreate(
                    exercise_id=test_exercise.id,
                    duration_min=Decimal("20")
                )
            ]
        )
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            ExerciseLogService.create_exercise_log(db_session, test_user.id, data)
        
        assert exc_info.value.status_code == 422
        assert "biometric" in str(exc_info.value.detail).lower()

    def test_get_daily_exercise_logs(
        self, 
        db_session, 
        test_user, 
        test_exercise, 
        test_biometric
    ):
        """Test lấy exercise logs trong ngày"""
        # Arrange
        today = datetime.now(timezone.utc)
        
        for _ in range(2):
            data = ExerciseLogEntryCreate(
                logged_at=today,
                items=[
                    ExerciseLogItemCreate(
                        exercise_id=test_exercise.id,
                        duration_min=Decimal("15")
                    )
                ]
            )
            ExerciseLogService.create_exercise_log(db_session, test_user.id, data)
        
        # Act
        entries = ExerciseLogService.get_daily_exercise_logs(
            db_session,
            test_user.id,
            today.date()
        )
        
        # Assert
        assert len(entries) == 2


    def test_update_exercise_log(
        self,
        db_session,
        test_user,
        test_exercise,
        test_biometric
    ):
        """Test cập nhật exercise log"""
        # Arrange
        original_time = datetime.now(timezone.utc)
        data = ExerciseLogEntryCreate(
            logged_at=original_time,
            items=[
                ExerciseLogItemCreate(
                    exercise_id=test_exercise.id,
                    duration_min=Decimal("20")
                )
            ]
        )
        entry = ExerciseLogService.create_exercise_log(db_session, test_user.id, data)
        original_calories = entry.total_calories
        
        # Act - Update logged_at
        from datetime import timedelta
        new_time = original_time + timedelta(hours=3)
        update_data = ExerciseLogEntryPatch(logged_at=new_time)
        updated_entry = ExerciseLogService.update_exercise_log(
            db_session,
            entry.id,
            test_user.id,
            update_data
        )
        
        # Assert
        assert updated_entry.logged_at == new_time
        # Items và calories không đổi
        assert updated_entry.total_calories == original_calories

    def test_update_exercise_log_item(
        self,
        db_session,
        test_user,
        test_exercise,
        test_biometric
    ):
        """Test cập nhật bài tập với ratio-based calculation"""
        # Arrange - Tạo entry với 30 phút
        data = ExerciseLogEntryCreate(
            logged_at=datetime.now(timezone.utc),
            items=[
                ExerciseLogItemCreate(
                    exercise_id=test_exercise.id,
                    duration_min=Decimal("30")  # 30 phút
                )
            ]
        )
        entry = ExerciseLogService.create_exercise_log(db_session, test_user.id, data)
        item_id = entry.items[0].id
        original_calories = entry.items[0].calories
        
        # Act - Giảm xuống 15 phút (1/2)
        update_data = ExerciseLogItemUpdate(duration_min=Decimal("15"))
        updated_item = ExerciseLogService.update_exercise_log_item(
            db_session,
            item_id,
            test_user.id,
            update_data
        )
        
        # Assert - Calories cũng phải giảm 1/2
        assert updated_item.duration_min == Decimal("15")
        expected_calories = original_calories * Decimal("0.5")
        assert updated_item.calories == round(expected_calories, 2)
        
        # Kiểm tra entry đã được re-aggregate
        db_session.refresh(entry)
        assert entry.total_calories == round(expected_calories, 2)


# ==================== DAILY SUMMARY TESTS ====================

class TestDailyLogService:
    """Test cases cho DailyLogService"""

    def test_get_daily_summary(
        self,
        db_session,
        test_user,
        test_food,
        test_exercise,
        test_biometric
    ):
        """Test tính tổng kết dinh dưỡng trong ngày"""
        # Arrange
        today = datetime.now(timezone.utc)
        
        # Tạo food log
        food_data = FoodLogEntryCreate(
            logged_at=today,
            meal_type=MealType.BREAKFAST,
            items=[
                FoodLogItemCreate(
                    food_id=test_food.id,
                    quantity=Decimal("1"),
                    unit="serving",
                    grams=Decimal("100")  # 265 kcal
                )
            ]
        )
        FoodLogService.create_food_log(db_session, test_user.id, food_data)
        
        # Tạo exercise log
        exercise_data = ExerciseLogEntryCreate(
            logged_at=today,
            items=[
                ExerciseLogItemCreate(
                    exercise_id=test_exercise.id,
                    duration_min=Decimal("30")  # 280 kcal
                )
            ]
        )
        ExerciseLogService.create_exercise_log(db_session, test_user.id, exercise_data)
        
        # Act
        summary = DailyLogService.get_daily_summary(
            db_session,
            test_user.id,
            today.date()
        )
        
        # Assert
        assert summary.total_calories_consumed == Decimal("265.00")
        assert summary.total_calories_burned == Decimal("280.00")
        assert summary.net_calories == Decimal("-15.00")  # 265 - 280
        assert summary.total_protein_g == Decimal("9.000")


# ==================== RUN TESTS ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])