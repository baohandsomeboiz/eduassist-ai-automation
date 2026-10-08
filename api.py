from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd

# 1. Khởi tạo ứng dụng FastAPI
app = FastAPI(title="EduAssist AI API", description="API dự đoán nguy cơ sinh viên rớt môn/bỏ học")

# 2. Load mô hình đã huấn luyện
try:
    model = joblib.load('xgboost_student_risk_model.pkl')
    # Tự động lấy danh sách các cột (features) mà mô hình yêu cầu từ lúc train
    expected_features = model.feature_names_in_
except Exception as e:
    print(f"Lỗi khi load mô hình: {e}")
    expected_features = []

# 3. Định nghĩa API Endpoint
@app.post("/predict")
def predict_risk(data: dict):
    """
    Nhận dữ liệu dạng JSON, tự động khớp với các cột của mô hình và trả về dự đoán.
    """
    # Tạo một DataFrame 1 dòng chứa toàn số 0 (mặc định) cho tất cả các cột
    input_df = pd.DataFrame(columns=expected_features)
    input_df.loc[0] = 0
    
    # Cập nhật các giá trị từ request người dùng gửi lên
    for key, value in data.items():
        if key in expected_features:
            input_df.at[0, key] = value
            
    # Ép kiểu về số thực để XGBoost không báo lỗi
    input_df = input_df.astype(float)
    
    # Chạy dự đoán
    prediction = model.predict(input_df)[0]
    probability = model.predict_proba(input_df)[0][1]
    
    # Trả về kết quả
    return {
        "risk_label": int(prediction),
        "risk_status": "Nguy cơ cao (Rớt/Bỏ học)" if prediction == 1 else "An toàn",
        "dropout_probability": f"{probability * 100:.2f}%"
    }