# EduAssist AI: Hệ thống Cảnh báo Học tập Toàn trường

Hệ thống End-to-End dự báo sớm nguy cơ rớt môn của sinh viên dựa trên hành vi học tập (LMS), tích hợp AI Backend, giao diện quản lý hàng loạt và tự động hóa bắn email cảnh báo qua n8n.

## Tính năng chính
- **Dự đoán cá nhân:** Kiểm tra nhanh nguy cơ rớt môn theo thời gian thực cho từng sinh viên.
- **Quét hàng loạt (Batch Processing):** Tải lên file CSV/Excel danh sách sinh viên từ hệ thống LMS để chấm điểm rủi ro toàn trường.
- **Tự động hóa (n8n Automation):** Kích hoạt webhook gửi email cảnh báo hàng loạt tới nhóm sinh viên có nguy cơ cao.

## Công nghệ sử dụng 
- **Machine Learning:** XGBoost, Scikit-learn
- **Backend API:** FastAPI
- **Frontend UI:** Streamlit
- **Automation Pipeline:** n8n (Webhook & SMTP Email)

##  Cấu trúc mã nguồn
- `api.py`: FastAPI server phục vụ mô hình dự đoán.
- `app.py`: Giao diện Streamlit đa tab (Cá nhân & Quét file hàng loạt).
- `main.ipynb`: Jupyter Notebook huấn luyện và tối ưu mô hình ML.
- `xgboost_student_risk_model.pkl`: Model AI đã huấn luyện.

##  Hướng dẫn chạy dự án
1. **Chạy Backend API:**
   ```bash
   uvicorn api:app --reload
