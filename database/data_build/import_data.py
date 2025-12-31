# pip install supabase pandas

import os
import json
import pandas as pd
from datetime import datetime, timezone
from supabase import create_client, Client

# ================= CẤU HÌNH =================
SUPABASE_URL = "https://ktxalsscztqdkvvpxldb.supabase.co"
SUPABASE_KEY = "sb_publishable_iP9ChxDmxdN8l7zXMirKMg_DGTBBUaS"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Đường dẫn file
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FOOD_FILE = os.path.join(CURRENT_DIR, "../data_food_exercise/cleaned_nutrients.json")
EXERCISE_FILE = os.path.join(CURRENT_DIR, "../data_food_exercise/fitness_activities_filtered.csv")

# ================= IMPORT FOOD (JSON) =================
def import_foods():
    """
    Import dữ liệu từ cleaned_nutrients.json vào 3 bảng:
    - foods: thông tin chung về thực phẩm
    - food_portions: khẩu phần ăn (1 food có nhiều portions)
    - food_nutrients: dinh dưỡng (1 food có nhiều nutrients)
    """
    print("=== IMPORT FOODS ===")
    try:
        with open(FOOD_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"Tong so thuc pham: {len(data)}")
        
        foods_batch = []
        portions_batch = []
        nutrients_batch = []
        batch_size = 50
        inserted_count = 0

        now = datetime.now(timezone.utc).isoformat()
        
        for idx, item in enumerate(data):
            try:
                # 1. Chuẩn bị dữ liệu cho bảng FOODS
                food_record = {
                    "owner_user_id": None,  # NULL = global data
                    "source_code": item.get('id'),  # Mã từ dataset (vd: "01001")
                    "name": item.get('name', 'Unknown'),
                    "food_group": item.get('group'),  # Nhóm thực phẩm
                    "deleted_at": None,
                    "created_at": now,
                    "updated_at": now
                }
                foods_batch.append(food_record)
                
                # 2. Chuẩn bị dữ liệu cho bảng FOOD_PORTIONS
                portions = item.get('portions', [])
                for portion in portions:
                    portion_record = {
                        "food_id": None,  # Sẽ cập nhật sau khi có food_id
                        "amount": portion.get('amount', 1.0),
                        "unit": portion.get('unit', 'g'),
                        "grams": portion.get('grams', 100.0),
                        "created_at": now,
                        "updated_at": now
                    }
                    portions_batch.append(portion_record)
                
                # 3. Chuẩn bị dữ liệu cho bảng FOOD_NUTRIENTS
                nutrients = item.get('nutrients', {})
                for nutrient_key, nutrient_data in nutrients.items():
                    # Chuyển key thành dạng: calories_kcal, protein_g, fat_g, ...
                    unit = nutrient_data.get('unit', '')
                    nutrient_name = f"{nutrient_key}_{unit}"
                    
                    nutrient_record = {
                        "food_id": None,  # Sẽ cập nhật sau khi có food_id
                        "nutrient_key": nutrient_name,
                        "amount_per_100g": nutrient_data.get('value', 0.0),
                        "created_at": now,
                        "updated_at": now
                    }
                    nutrients_batch.append(nutrient_record)
                
                # Batch insert khi đủ kích thước
                if len(foods_batch) >= batch_size:
                    # Insert foods trước
                    response = supabase.table("foods").insert(foods_batch).execute()
                    inserted_foods = response.data
                    
                    # Lấy mapping: index -> food_id
                    food_id_map = {}
                    for i, food in enumerate(inserted_foods):
                        food_id_map[inserted_count + i] = food['id']
                    
                    # Cập nhật food_id cho portions và nutrients
                    portion_start_idx = 0
                    nutrient_start_idx = 0
                    
                    for i in range(len(foods_batch)):
                        food_idx = inserted_count + i
                        food_id = food_id_map[food_idx]
                        
                        # Tính số portions của food này
                        original_item = data[food_idx]
                        num_portions = len(original_item.get('portions', []))
                        
                        # Gán food_id cho portions
                        for j in range(portion_start_idx, portion_start_idx + num_portions):
                            if j < len(portions_batch):
                                portions_batch[j]['food_id'] = food_id
                        portion_start_idx += num_portions
                        
                        # Tính số nutrients của food này
                        num_nutrients = len(original_item.get('nutrients', {}))
                        
                        # Gán food_id cho nutrients
                        for j in range(nutrient_start_idx, nutrient_start_idx + num_nutrients):
                            if j < len(nutrients_batch):
                                nutrients_batch[j]['food_id'] = food_id
                        nutrient_start_idx += num_nutrients
                    
                    # Insert portions nếu có
                    if portions_batch:
                        valid_portions = [p for p in portions_batch if p['food_id'] is not None]
                        if valid_portions:
                            supabase.table("food_portions").insert(valid_portions).execute()
                    
                    # Insert nutrients nếu có
                    if nutrients_batch:
                        valid_nutrients = [n for n in nutrients_batch if n['food_id'] is not None]
                        if valid_nutrients:
                            supabase.table("food_nutrients").insert(valid_nutrients).execute()
                    
                    inserted_count += len(foods_batch)
                    print(f"Da nhap {inserted_count}/{len(data)} thuc pham ({inserted_count/len(data)*100:.1f}%)")
                    
                    # Reset batch
                    foods_batch = []
                    portions_batch = []
                    nutrients_batch = []
                    
            except Exception as item_error:
                print(f"Loi xu ly muc {idx}: {item_error}")
        
        # Insert phần còn lại
        if foods_batch:
            response = supabase.table("foods").insert(foods_batch).execute()
            inserted_foods = response.data
            
            food_id_map = {}
            for i, food in enumerate(inserted_foods):
                food_id_map[inserted_count + i] = food['id']
            
            portion_start_idx = 0
            nutrient_start_idx = 0
            
            for i in range(len(foods_batch)):
                food_idx = inserted_count + i
                food_id = food_id_map[food_idx]
                
                original_item = data[food_idx]
                num_portions = len(original_item.get('portions', []))
                
                for j in range(portion_start_idx, portion_start_idx + num_portions):
                    if j < len(portions_batch):
                        portions_batch[j]['food_id'] = food_id
                portion_start_idx += num_portions
                
                num_nutrients = len(original_item.get('nutrients', {}))
                
                for j in range(nutrient_start_idx, nutrient_start_idx + num_nutrients):
                    if j < len(nutrients_batch):
                        nutrients_batch[j]['food_id'] = food_id
                nutrient_start_idx += num_nutrients
            
            if portions_batch:
                valid_portions = [p for p in portions_batch if p['food_id'] is not None]
                if valid_portions:
                    supabase.table("food_portions").insert(valid_portions).execute()
            
            if nutrients_batch:
                valid_nutrients = [n for n in nutrients_batch if n['food_id'] is not None]
                if valid_nutrients:
                    supabase.table("food_nutrients").insert(valid_nutrients).execute()
            
            inserted_count += len(foods_batch)
            print(f"Da nhap {inserted_count} thuc pham hoan toan")
        
        print(f"\nHOAN TAT FOODS! Nhap thanh cong: {inserted_count} thuc pham")
        
    except FileNotFoundError:
        print(f"Khong tim thay file: {FOOD_FILE}")
    except json.JSONDecodeError as e:
        print(f"Loi JSON: {e}")
    except Exception as e:
        print(f"Loi nhap lieu bang Foods: {e}")
        import traceback
        traceback.print_exc()


# ================= IMPORT EXERCISE (CSV) =================
def import_exercises():
    """
    Import dữ liệu từ fitness_activities_filtered.csv vào bảng exercises
    """
    print("\n=== IMPORT EXERCISES ===")
    try:
        if not os.path.exists(EXERCISE_FILE):
            print(f"Khong tim thay file: {EXERCISE_FILE}")
            return

        df = pd.read_csv(EXERCISE_FILE)
        print(f"Tong so bai tap: {len(df)}")
        
        now = datetime.now(timezone.utc).isoformat()

        # Chuẩn bị dữ liệu theo schema của model Exercise
        records = []
        for idx, row in df.iterrows():
            record = {
                "owner_user_id": None,  # NULL = global data
                "activity_code": str(row['Activity Code']),  # Mã hoạt động
                "major_heading": row['Major Heading'],  # Nhóm bài tập
                "description": row['Activity Description'],  # Mô tả bài tập
                "met_value": float(row['MET Value']),  # Giá trị MET
                "deleted_at": None,
                "created_at": now,
                "updated_at": now
            }
            records.append(record)
        
        # Insert theo batch
        batch_size = 100
        inserted_count = 0
        for i in range(0, len(records), batch_size):
            batch = records[i:i+batch_size]
            supabase.table("exercises").insert(batch).execute()
            inserted_count += len(batch)
            print(f"Da nhap {inserted_count}/{len(records)} bai tap ({inserted_count/len(records)*100:.1f}%)")
        
        print(f"\nHOAN TAT EXERCISES! Nhap thanh cong: {len(records)} bai tap")

    except Exception as e:
        print(f"Loi nhap lieu bang Exercises: {e}")
        import traceback
        traceback.print_exc()


# ================= MAIN =================
if __name__ == "__main__":
    print("BAT DAU IMPORT DU LIEU LEN SUPABASE...\n")
    
    # Import Foods (và portions, nutrients)
    import_foods()
    
    # Import Exercises
    import_exercises()
    
    print("\n" + "="*50)
    print("HOAN TAT TAI LEN TAT CA DU LIEU!")
    print("="*50)