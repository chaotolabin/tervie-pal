"""
Unit Tests cho Exercise Module
Sử dụng mocks thay vì database thật
"""
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException

from app.main import app
from app.models.exercise import Exercise


# ===== Test Configuration =====

client = TestClient(app)

TEST_USER_ID = uuid.UUID("128283af-efdd-4359-90d4-a071754fdfff")


# ===== Mock Data Factories =====

def create_mock_exercise(
    exercise_id: int = 1,
    owner_user_id: uuid.UUID = None,
    activity_code: str = None,
    major_heading: str = "Running",
    description: str = "Running, 5 mph (12 min/mile)",
    met_value: Decimal = Decimal("8.3"),
    deleted_at: datetime = None
) -> Mock:
    """Tạo mock Exercise object"""
    exercise = Mock(spec=Exercise)
    exercise.id = exercise_id
    exercise.owner_user_id = owner_user_id
    exercise.activity_code = activity_code
    exercise.major_heading = major_heading
    exercise.description = description
    exercise.met_value = met_value
    exercise.deleted_at = deleted_at
    return exercise


# ===== Test Cases =====

class TestSearchExercises:
    """Test GET /exercises/search"""
    
    @patch('app.services.exercise_service.ExerciseService.search_exercises')
    @patch('app.api.deps.get_current_user')
    @patch('app.core.database.get_db')
    def test_search_exercises_success(self, mock_get_db, mock_get_user, mock_search):
        """Test tìm kiếm exercises thành công"""
        # Setup mocks
        mock_user = Mock()
        mock_user.id = TEST_USER_ID
        mock_get_user.return_value = mock_user
        mock_get_db.return_value = Mock()
        
        # Mock service return
        mock_exercise = create_mock_exercise()
        mock_search.return_value = ([mock_exercise], None)
        
        # Call API
        response = client.get("/api/v1/exercises/search?q=running")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "next_cursor" in data
        assert len(data["items"]) == 1
        assert data["items"][0]["description"] == "Running, 5 mph (12 min/mile)"
        assert float(data["items"][0]["met_value"]) == 8.3
    
    @patch('app.services.exercise_service.ExerciseService.search_exercises')
    @patch('app.api.deps.get_current_user')
    @patch('app.core.database.get_db')
    def test_search_no_results(self, mock_get_db, mock_get_user, mock_search):
        """Test tìm kiếm không có kết quả"""
        mock_user = Mock()
        mock_user.id = TEST_USER_ID
        mock_get_user.return_value = mock_user
        mock_get_db.return_value = Mock()
        mock_search.return_value = ([], None)
        
        response = client.get("/api/v1/exercises/search?q=xyz123")
        
        assert response.status_code == 200
        assert len(response.json()["items"]) == 0
    
    @patch('app.services.exercise_service.ExerciseService.search_exercises')
    @patch('app.api.deps.get_current_user')
    @patch('app.core.database.get_db')
    def test_search_with_major_heading_filter(self, mock_get_db, mock_get_user, mock_search):
        """Test tìm kiếm có lọc theo major_heading"""
        mock_user = Mock()
        mock_user.id = TEST_USER_ID
        mock_get_user.return_value = mock_user
        mock_get_db.return_value = Mock()
        
        mock_exercises = [
            create_mock_exercise(1, major_heading="Swimming", description="Swimming laps, freestyle, fast"),
            create_mock_exercise(2, major_heading="Swimming", description="Swimming, treading water, moderate")
        ]
        mock_search.return_value = (mock_exercises, None)
        
        response = client.get("/api/v1/exercises/search?q=swim&major_heading=Swimming")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        # Verify mock được gọi với major_heading
        mock_search.assert_called_once()
        call_kwargs = mock_search.call_args[1]
        assert call_kwargs["major_heading"] == "Swimming"


class TestCreateExercise:
    """Test POST /exercises"""
    
    @patch('app.services.exercise_service.ExerciseService.create_exercise')
    @patch('app.api.deps.get_current_user')
    @patch('app.core.database.get_db')
    def test_create_exercise_success(self, mock_get_db, mock_get_user, mock_create):
        """Test tạo exercise thành công"""
        mock_user = Mock()
        mock_user.id = TEST_USER_ID
        mock_get_user.return_value = mock_user
        mock_get_db.return_value = Mock()
        
        # Mock created exercise
        mock_exercise = create_mock_exercise(
            exercise_id=100,
            owner_user_id=TEST_USER_ID,
            description="My custom running",
            major_heading="Running",
            met_value=Decimal("7.5")
        )
        mock_create.return_value = mock_exercise
        
        request_data = {
            "description": "My custom running",
            "major_heading": "Running",
            "met_value": 7.5
        }
        
        response = client.post("/api/v1/exercises", json=request_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["description"] == "My custom running"
        assert data["owner_user_id"] == str(TEST_USER_ID)
        assert float(data["met_value"]) == 7.5
    
    @patch('app.api.deps.get_current_user')
    @patch('app.core.database.get_db')
    def test_create_exercise_invalid_met_value(self, mock_get_db, mock_get_user):
        """Test tạo exercise với MET value không hợp lệ"""
        mock_user = Mock()
        mock_user.id = TEST_USER_ID
        mock_get_user.return_value = mock_user
        mock_get_db.return_value = Mock()
        
        request_data = {
            "description": "Invalid exercise",
            "met_value": -1.0  # MET âm
        }
        
        response = client.post("/api/v1/exercises", json=request_data)
        
        assert response.status_code == 422


class TestGetExercise:
    """Test GET /exercises/{exercise_id}"""
    
    @patch('app.services.exercise_service.ExerciseService.get_exercise_by_id')
    @patch('app.api.deps.get_current_user')
    @patch('app.core.database.get_db')
    def test_get_global_exercise(self, mock_get_db, mock_get_user, mock_get_ex):
        """Test lấy global exercise"""
        mock_user = Mock()
        mock_user.id = TEST_USER_ID
        mock_get_user.return_value = mock_user
        mock_get_db.return_value = Mock()
        
        mock_exercise = create_mock_exercise(owner_user_id=None)
        mock_get_ex.return_value = mock_exercise
        
        response = client.get("/api/v1/exercises/1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["owner_user_id"] is None
    
    @patch('app.services.exercise_service.ExerciseService.get_exercise_by_id')
    @patch('app.api.deps.get_current_user')
    @patch('app.core.database.get_db')
    def test_get_exercise_not_found(self, mock_get_db, mock_get_user, mock_get_ex):
        """Test lấy exercise không tồn tại"""
        mock_user = Mock()
        mock_user.id = TEST_USER_ID
        mock_get_user.return_value = mock_user
        mock_get_db.return_value = Mock()
        mock_get_ex.side_effect = HTTPException(status_code=404, detail="Exercise not found")
        
        response = client.get("/api/v1/exercises/999")
        
        assert response.status_code == 404


class TestUpdateExercise:
    """Test PATCH /exercises/{exercise_id}"""
    
    @patch('app.services.exercise_service.ExerciseService.update_exercise')
    @patch('app.api.deps.get_current_user')
    @patch('app.core.database.get_db')
    def test_update_own_exercise_success(self, mock_get_db, mock_get_user, mock_update):
        """Test update custom exercise của mình thành công"""
        mock_user = Mock()
        mock_user.id = TEST_USER_ID
        mock_get_user.return_value = mock_user
        mock_get_db.return_value = Mock()
        
        # Mock updated exercise
        updated_exercise = create_mock_exercise(
            exercise_id=100,
            owner_user_id=TEST_USER_ID,
            description="Updated description",
            met_value=Decimal("9.0")
        )
        mock_update.return_value = updated_exercise
        
        update_data = {
            "description": "Updated description",
            "met_value": 9.0
        }
        response = client.patch("/api/v1/exercises/100", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated description"
        assert float(data["met_value"]) == 9.0
    
    @patch('app.services.exercise_service.ExerciseService.update_exercise')
    @patch('app.api.deps.get_current_user')
    @patch('app.core.database.get_db')
    def test_update_global_exercise_forbidden(self, mock_get_db, mock_get_user, mock_update):
        """Test không được update global exercise"""
        mock_user = Mock()
        mock_user.id = TEST_USER_ID
        mock_get_user.return_value = mock_user
        mock_get_db.return_value = Mock()
        mock_update.side_effect = HTTPException(status_code=403, detail="Cannot update global exercise")
        
        response = client.patch("/api/v1/exercises/1", json={"description": "Hacked"})
        
        assert response.status_code == 403


class TestDeleteExercise:
    """Test DELETE /exercises/{exercise_id}"""
    
    @patch('app.services.exercise_service.ExerciseService.delete_exercise')
    @patch('app.api.deps.get_current_user')
    @patch('app.core.database.get_db')
    def test_delete_own_exercise_success(self, mock_get_db, mock_get_user, mock_delete):
        """Test xóa custom exercise của mình thành công"""
        mock_user = Mock()
        mock_user.id = TEST_USER_ID
        mock_get_user.return_value = mock_user
        mock_get_db.return_value = Mock()
        mock_delete.return_value = None
        
        response = client.delete("/api/v1/exercises/100")
        
        assert response.status_code == 204
    
    @patch('app.services.exercise_service.ExerciseService.delete_exercise')
    @patch('app.api.deps.get_current_user')
    @patch('app.core.database.get_db')
    def test_delete_global_exercise_forbidden(self, mock_get_db, mock_get_user, mock_delete):
        """Test không được xóa global exercise"""        
        mock_user = Mock()
        mock_user.id = TEST_USER_ID
        mock_get_user.return_value = mock_user
        mock_get_db.return_value = Mock()
        mock_delete.side_effect = HTTPException(status_code=403, detail="Cannot delete global exercise")
        
        response = client.delete("/api/v1/exercises/1")
        
        assert response.status_code == 403


class TestCalculateCalories:
    """Test utility function calculate_calories_burned"""
    
    def test_calculate_calories_normal(self):
        """Test tính calories bình thường"""
        from app.services.exercise_service import ExerciseService
        
        # MET = 8.0, weight = 70kg, duration = 30 minutes
        calories = ExerciseService.calculate_calories_burned(
            met_value=Decimal("8.0"),
            weight_kg=70,
            duration_minutes=30
        )
        
        # Expected: 8.0 * 70 * 0.5 = 280 kcal
        assert calories == 280.0
    
    def test_calculate_calories_one_hour(self):
        """Test tính calories cho 1 giờ"""
        from app.services.exercise_service import ExerciseService
        
        # MET = 5.0, weight = 60kg, duration = 60 minutes
        calories = ExerciseService.calculate_calories_burned(
            met_value=Decimal("5.0"),
            weight_kg=60,
            duration_minutes=60
        )
        
        # Expected: 5.0 * 60 * 1.0 = 300 kcal
        assert calories == 300.0