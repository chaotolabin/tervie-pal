# Daily Logs API Documentation

## 📋 Tổng quan

Tính năng Daily Logging cho phép người dùng ghi lại và theo dõi:
- **Food Logs**: Các bữa ăn hàng ngày (breakfast, lunch, dinner, snacks)
- **Exercise Logs**: Các buổi tập luyện
- **Daily Summary**: Tổng kết dinh dưỡng và calories trong ngày

---

## 🏗️ Kiến trúc

### **1. Database Schema**

```
FoodLogEntry (Bữa ăn)
├── id (PK)
├── user_id (FK)
├── logged_at (datetime)
├── meal_type (breakfast/lunch/dinner/snacks)
├── total_calories ← Tổng hợp từ items
├── total_protein_g
├── total_carbs_g
├── total_fat_g
└── items → FoodLogItem[]

FoodLogItem (Chi tiết món ăn)
├── id (PK)
├── entry_id (FK)
├── food_id (FK)
├── portion_id (FK, nullable)
├── quantity
├── unit
├── grams
├── calories ← Snapshot (đã tính theo grams)
├── protein_g
├── carbs_g
└── fat_g

ExerciseLogEntry (Buổi tập)
├── id (PK)
├── user_id (FK)
├── logged_at (datetime)
├── total_calories ← Tổng hợp từ items
└── items → ExerciseLogItem[]

ExerciseLogItem (Chi tiết bài tập)
├── id (PK)
├── entry_id (FK)
├── exercise_id (FK)
├── duration_min
├── met_value_snapshot ← Snapshot
├── calories ← Đã tính
└── notes
```

### **2. Business Logic Flow**

#### **Food Log Creation:**
```
1. Client gửi: logged_at, meal_type, items[{food_id, grams, ...}]
2. Server query Food → lấy nutrients (calories, protein, carbs, fat per 100g)
3. Tính dinh dưỡng theo grams: (grams / 100) × nutrient_per_100g
4. Lưu snapshot vào FoodLogItem
5. Tổng hợp tất cả items → Lưu vào FoodLogEntry
6. Commit transaction
```

#### **Exercise Log Creation:**
```
1. Client gửi: logged_at, items[{exercise_id, duration_min, ...}]
2. Server query BiometricsLog → lấy cân nặng mới nhất
3. Server query Exercise → lấy met_value
4. Tính calories: MET × weight(kg) × duration(hours)
5. Lưu snapshot (met_value, calories) vào ExerciseLogItem
6. Tổng hợp → Lưu vào ExerciseLogEntry
7. Commit transaction
```

---

## 🔌 API Endpoints

### **Base URL:** `/api/v1/logs`

---

### **1. Food Logs**

#### **POST /food** - Tạo log bữa ăn mới

**Request Body:**
```json
{
  "logged_at": "2023-10-27T08:00:00+07:00",
  "meal_type": "breakfast",
  "items": [
    {
      "food_id": 1,
      "quantity": 2,
      "unit": "slice",
      "grams": 60,
      "portion_id": null
    },
    {
      "food_id": 2,
      "quantity": 1,
      "unit": "cup",
      "grams": 200
    }
  ]
}
```

**Response (201):**
```json
{
  "id": 123,
  "user_id": "uuid...",
  "logged_at": "2023-10-27T08:00:00+07:00",
  "meal_type": "breakfast",
  "total_calories": 450.50,
  "total_protein_g": 15.200,
  "total_carbs_g": 60.000,
  "total_fat_g": 10.500,
  "created_at": "2023-10-27T01:30:00Z",
  "updated_at": null,
  "deleted_at": null,
  "items": [
    {
      "id": 456,
      "entry_id": 123,
      "food_id": 1,
      "portion_id": null,
      "quantity": 2,
      "unit": "slice",
      "grams": 60,
      "calories": 159.00,
      "protein_g": 5.400,
      "carbs_g": 29.400,
      "fat_g": 1.920
    }
  ]
}
```

---

#### **GET /food/daily/{date}** - Lấy tất cả bữa ăn trong ngày

**URL:** `/api/v1/logs/food/daily/2023-10-27`

**Response (200):**
```json
[
  {
    "id": 123,
    "meal_type": "breakfast",
    "total_calories": 450.50,
    "items": [...]
  },
  {
    "id": 124,
    "meal_type": "lunch",
    "total_calories": 600.00,
    "items": [...]
  }
]
```

---

#### **GET /food/{entry_id}** - Lấy chi tiết 1 bữa ăn

**URL:** `/api/v1/logs/food/123`

**Response (200):** Giống POST response

---

#### **PATCH /food/{entry_id}** - Cập nhật bữa ăn

**URL:** `/api/v1/logs/food/123`

**Request Body:**
```json
{
  "logged_at": "2023-10-27T09:00:00+07:00",
  "meal_type": "lunch"
}
```

**Note:** 
- Chỉ có thể update `logged_at` và `meal_type`
- Không thể thay đổi items (món ăn)
- Nếu muốn thay đổi items, phải xóa và tạo mới
- Chỉ update các field không null trong request (partial update)

**Response (200):** FoodLogEntryResponse với giá trị mới

---

#### **DELETE /food/{entry_id}** - Xóa bữa ăn

**Response (204):** No Content

---

### **2. Exercise Logs**

#### **POST /exercise** - Tạo log buổi tập mới

**Request Body:**
```json
{
  "logged_at": "2023-10-27T18:00:00+07:00",
  "items": [
    {
      "exercise_id": 10,
      "duration_min": 30,
      "notes": "Running at moderate pace"
    },
    {
      "exercise_id": 15,
      "duration_min": 20,
      "notes": "Cycling"
    }
  ]
}
```

**Response (201):**
```json
{
  "id": 200,
  "user_id": "uuid...",
  "logged_at": "2023-10-27T18:00:00+07:00",
  "total_calories": 480.00,
  "created_at": "2023-10-27T11:30:00Z",
  "updated_at": null,
  "deleted_at": null,
  "items": [
    {
      "id": 500,
      "entry_id": 200,
      "exercise_id": 10,
      "duration_min": 30,
      "met_value_snapshot": 8.0,
      "calories": 280.00,
      "notes": "Running at moderate pace"
    }
  ]
}
```

---

#### **GET /exercise/daily/{date}** - Lấy tất cả buổi tập trong ngày

**URL:** `/api/v1/logs/exercise/daily/2023-10-27`

**Response (200):** Array of ExerciseLogEntry

---

#### **GET /exercise/{entry_id}** - Lấy chi tiết 1 buổi tập

**URL:** `/api/v1/logs/exercise/200`

---

#### **PATCH /exercise/{entry_id}** - Cập nhật buổi tập

**URL:** `/api/v1/logs/exercise/200`

**Request Body:**
```json
{
  "logged_at": "2023-10-27T19:00:00+07:00"
}
```

**Note:**
- Chỉ có thể update `logged_at`
- Không thể thay đổi items (bài tập)
- Nếu muốn thay đổi items, phải xóa và tạo mới

**Response (200):** ExerciseLogEntryResponse với giá trị mới

---

#### **DELETE /exercise/{entry_id}** - Xóa buổi tập

**Response (204):** No Content

---

### **3. Daily Summary**

#### **GET /daily/{date}** - Lấy tất cả logs và tổng kết

**URL:** `/api/v1/logs/daily/2023-10-27`

**Response (200):**
```json
{
  "date": "2023-10-27",
  "food_logs": [...],
  "exercise_logs": [...],
  "summary": {
    "date": "2023-10-27",
    "total_calories_consumed": 1850.50,
    "total_calories_burned": 480.00,
    "net_calories": 1370.50,
    "total_protein_g": 75.200,
    "total_carbs_g": 210.500,
    "total_fat_g": 55.300
  }
}
```

---

#### **GET /summary/{date}** - Chỉ lấy tổng kết (không có chi tiết logs)

**URL:** `/api/v1/logs/summary/2023-10-27`

**Response (200):** DailyNutritionSummary object

---

## 🧮 Công thức tính toán

### **1. Dinh dưỡng Food**

```python
# Lấy nutrient_per_100g từ bảng FoodNutrient
# Tính theo grams thực tế:
multiplier = grams / 100

item_calories = nutrient_calories_per_100g × multiplier
item_protein = nutrient_protein_per_100g × multiplier
item_carbs = nutrient_carbs_per_100g × multiplier
item_fat = nutrient_fat_per_100g × multiplier

# Tổng hợp:
entry.total_calories = sum(item.calories for item in items)
```

### **2. Calories Burned (Exercise)**

```python
# Công thức MET:
duration_hours = duration_min / 60
calories_burned = met_value × weight_kg × duration_hours

# Ví dụ:
# MET = 8.0 (Running moderate)
# Weight = 70 kg
# Duration = 30 min = 0.5 hours
# Calories = 8.0 × 70 × 0.5 = 280 kcal
```

---

## 📝 Lưu ý quan trọng

### **1. Snapshot Pattern**
- **Mục đích:** Giữ nguyên lịch sử dù data gốc (Food/Exercise) có thay đổi
- **FoodLogItem:** Lưu `calories`, `protein_g`, `carbs_g`, `fat_g` đã tính
- **ExerciseLogItem:** Lưu `met_value_snapshot`, `calories` đã tính

### **2. Transaction Safety**
- Tạo Entry và Items trong cùng 1 transaction
- Nếu lỗi ở bất kỳ item nào → Rollback toàn bộ

### **3. Performance Optimization**
- Sử dụng `selectinload()` để eager load items → Tránh N+1 query
- Tính toán ở Service Layer, không để Frontend tự tính

### **4. Validation Rules**
- **Food Log:**
  - Bữa ăn phải có ≥ 1 món
  - Food ID phải tồn tại và chưa xóa
  - Grams, quantity > 0
  
- **Exercise Log:**
  - Buổi tập phải có ≥ 1 bài tập
  - Exercise ID phải tồn tại và chưa xóa
  - Duration > 0
  - User phải có ≥ 1 biometric log (để lấy cân nặng)

---

## 🧪 Testing

### **Chạy tests:**
```bash
cd backend
pytest app/tests/test_logs.py -v
```

### **Test Coverage:**
- ✅ Create food log với single item
- ✅ Create food log với multiple items
- ✅ Validate invalid food_id
- ✅ Get daily food logs
- ✅ Delete food log (soft delete)
- ✅ Create exercise log với biometric data
- ✅ Validate missing biometric data
- ✅ Get daily exercise logs
- ✅ Daily summary calculation

---

## 🚀 Next Steps

### **Tính năng mở rộng:**
1. ~~**Edit Log:** PATCH endpoint để sửa entry (meal_type, logged_at)~~ ✅ **Đã hoàn thành**
2. **Add/Remove Items:** PUT endpoint để thêm/xóa item trong entry hiện có
3. **Copy Logs:** Sao chép bữa ăn/buổi tập sang ngày khác
4. **Templates:** Lưu meal templates để tái sử dụng
5. **Batch Delete:** Xóa nhiều entries cùng lúc
6. **Date Range Query:** Lấy logs trong khoảng thời gian (1 tuần, 1 tháng)
7. **Statistics:** Biểu đồ calories trends, macros distribution

### **Performance Optimization:**
1. **Caching:** Cache daily summary với Redis (TTL: 5 phút)
2. **Indexes:** Thêm composite index cho (user_id, logged_at, deleted_at)
3. **Pagination:** Thêm cursor pagination cho GET /food và /exercise

### **Security:**
1. **Rate Limiting:** Giới hạn số lượng logs/ngày
2. **Input Sanitization:** Validate notes field (XSS prevention)

---

## 📚 Tài liệu tham khảo

- **MET Values:** [Compendium of Physical Activities](https://sites.google.com/site/compendiumofphysicalactivities/)
- **Nutrition Database:** USDA FoodData Central
- **BMR Formula:** Mifflin-St Jeor Equation (xem biometric_service.py)
