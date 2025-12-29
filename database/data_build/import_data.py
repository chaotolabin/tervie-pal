# pip install supabase pandas

import os
import json
import pandas as pd
from supabase import create_client, Client

# ================= CẤU HÌNH =================
SUPABASE_URL = "https://ktxalsscztqdkvvpxldb.supabase.co"
SUPABASE_KEY = "sb_publishable_iP9ChxDmxdN8l7zXMirKMg_DGTBBUaS"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Đường dẫn file
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FOOD_FILE = os.path.join(CURRENT_DIR, "../data/cleaned_nutrients.json") # File JSON
# EXERCISE_FILE = os.path.join(CURRENT_DIR, "../data/exercise_data.csv") # File CSV

# ================= IMPORT FOOD (JSON) =================
def import_foods():
    print("Dang xu ly du lieu Food...")
    try:
        with open(FOOD_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"Tong so muc: {len(data)}")
        
        batch = []
        batch_size = 100
        inserted_count = 0
        failed_items = []
        
        for idx, item in enumerate(data):
            try:
                raw_name = item.get('name', 'Unknown')
                food_name = 'Unknown'
                
                if isinstance(raw_name, dict):
                    # Dữ liệu gốc --> lấy trường long 
                    food_name = raw_name.get('long', 'Unknown')
                else:
                    # Dữ liệu đã làm sạch --> trực tiếp chuyển sang chuỗi
                    food_name = str(raw_name)

                record = {
                    # Không cần id vì Supabase sẽ tự tạo
                    "original_id": item.get('id', None),
                    "name": food_name,
                    "group": item.get('group', 'Other'),
                    "content": item # Cột JSONB lưu toàn bộ dữ liệu
                }
                batch.append(record)
                
                # Batch insert
                if len(batch) >= batch_size:
                    try:
                        # Tải DL vào bảng foods
                        response = supabase.table("foods").insert(batch).execute()
                        inserted_count += len(batch)
                        print(f"Da nhap {inserted_count} muc... ({(idx+1)/len(data)*100:.1f}%)")
                    except Exception as batch_error:
                        print(f"Loi batch tai dong {idx}: {batch_error}")
                        failed_items.extend(batch)
                    batch = [] # Reset batch
            except Exception as item_error:
                print(f"Loi xu ly muc tai dong {idx}: {item_error}")
                failed_items.append(item)
        
        # Insert nốt số dư
        if batch:
            try:
                response = supabase.table("foods").insert(batch).execute()
                inserted_count += len(batch)
                print(f"Da nhap {inserted_count} muc hoan toan")
            except Exception as final_error:
                print(f"Loi batch cuoi cung: {final_error}")
                failed_items.extend(batch)
        
        print(f"\nHoan tat! Nhap thanh cong: {inserted_count}/{len(data)}")
        if failed_items:
            print(f"That bai: {len(failed_items)} muc")
        
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
    print("Dang xu ly du lieu Exercise...")
    try:
        # Đọc file CSV
        # Cần đảm bảo file CSV tồn tại và biến EXERCISE_FILE được uncomment ở trên
        if 'EXERCISE_FILE' not in globals() or not os.path.exists(EXERCISE_FILE):
             print("Chua cau hinh duong dan file CSV")
             return

        df = pd.read_csv(EXERCISE_FILE)
        
        # Làm sạch dữ liệu (sửa sau nếu cần)
        df = df.dropna(subset=['activity']) 
        
        # Chuyển đổi tên cột CSV sang tên cột Supabase (nếu khác nhau)
        df = df.rename(columns={
            "Activity": "name",
            "Type": "type", # Cardio/Strength
            "Met_Value": "met_value" # Chỉ số để tính calo
        })
        
        # Chuyển DataFrame thành List of Dictionaries
        records = df.to_dict(orient='records')
        
        # Đẩy lên Supabase
        chunk_size = 100
        for i in range(0, len(records), chunk_size):
            chunk = records[i:i+chunk_size]
            supabase.table("exercises").insert(chunk).execute()
            
        print(f"Da nhap xong bang Exercises ({len(records)} bai tap)!")

    except Exception as e:
        print(f"Loi nhap lieu bang Exercises: {e}")

# ================= MAIN =================
if __name__ == "__main__":
    import_foods()
    # import_exercises()
    print("HOAN TAT TAI LEN!")