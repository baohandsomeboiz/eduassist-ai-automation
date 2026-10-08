import streamlit as st
import requests
import pandas as pd

# 1. Cấu hình trang
st.set_page_config(page_title="EduAssist AI - Quản lý Hàng loạt", layout="wide")
st.title("🎓 EduAssist AI: Hệ thống Cảnh báo Học tập Toàn trường")

# Tạo 2 Tab để linh hoạt giữa nhập đơn lẻ hoặc quét file hàng loạt
tab1, tab2 = st.tabs(["👤 Dự đoán cá nhân (Demo)", "📁 Quét danh sách sinh viên hàng loạt (File CSV/Excel)"])

# --- TAB 1: DỰ ĐOÁN CÁ NHÂN ---
with tab1:
    with st.form("predict_form"):
        st.subheader("Nhập thông tin hành vi của một sinh viên:")
        student_email = st.text_input("Email sinh viên", "sinhvien@example.edu.vn")
        
        col1, col2 = st.columns(2)
        with col1:
            studied_credits = st.number_input("Số tín chỉ đang học", min_value=0, max_value=120, value=60)
            gender = st.selectbox("Giới tính", ["Nam", "Nữ"])
        with col2:
            total_lms_clicks = st.number_input("Tổng số lần click hệ thống LMS", min_value=0, value=15)
            
        submit = st.form_submit_button("Dự đoán Nguy Cơ")

    if submit:
        gender_M = 1 if gender == "Nam" else 0
        payload = {"studied_credits": studied_credits, "total_lms_clicks": total_lms_clicks, "gender_M": gender_M}
        try:
            response = requests.post("http://127.0.0.1:8000/predict", json=payload)
            if response.status_code == 200:
                result = response.json()
                st.markdown("---")
                if result["risk_label"] == 1:
                    st.error(f"⚠️ **{result['risk_status']}** (Tỷ lệ rủi ro: {result['dropout_probability']})")
                    
                    # Gửi Webhook đơn lẻ qua n8n
                    webhook_url = "http://localhost:5678/webhook/88704c7c-2610-4a25-9a94-600f1edc1d28" # Link Production
                    n8n_payload = {"email": student_email, "risk_prob": result["dropout_probability"], "message": "Cảnh báo nguy cơ rớt môn!"}
                    try:
                        resp = requests.post(webhook_url, json=n8n_payload)
                        if resp.status_code == 200:
                            st.success("✅ Đã tự động gửi Email cảnh báo qua n8n!")
                        else:
                            st.error(f"❌ n8n phản hồi lỗi mã: {resp.status_code}")
                    except Exception as ex:
                        st.error(f"❌ Không thể gọi Webhook n8n: {ex}")
                else:
                    st.success(f"✅ **{result['risk_status']}** (Tỷ lệ rủi ro: {result['dropout_probability']})")
        except Exception as e:
            st.error(f"Lỗi kết nối Backend AI: {e}")

# --- TAB 2: QUÉT HÀNG LOẠT TỪ FILE ---
with tab2:
    st.subheader("📁 Tải lên danh sách sinh viên từ hệ thống LMS")
    st.write("File tải lên cần có các cột: `email`, `studied_credits`, `total_lms_clicks`, `gender` (Nam/Nữ)")
    
    uploaded_file = st.file_uploader("Chọn file CSV hoặc Excel", type=["csv", "xlsx"], key="file_upload_tab2")
    
    if uploaded_file is not None:
        # Đọc file bằng Pandas
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
            
        st.write("📊 **Xem trước dữ liệu gốc (5 dòng đầu):**", df.head())
        
        if st.button("🚀 Chạy phân tích rủi ro toàn bộ danh sách"):
            risk_results = []
            
            # Vòng lặp qua từng sinh viên trong file
            for index, row in df.iterrows():
                g_val = 1 if str(row.get("gender", "Nam")).strip() == "Nam" else 0
                payload = {
                    "studied_credits": int(row.get("studied_credits", 60)),
                    "total_lms_clicks": int(row.get("total_lms_clicks", 15)),
                    "gender_M": g_val
                }
                
                try:
                    res = requests.post("http://127.0.0.1:8000/predict", json=payload)
                    if res.status_code == 200:
                        data = res.json()
                        risk_results.append({
                            "email": row.get("email", "unknown@edu.vn"),
                            "studied_credits": row.get("studied_credits"),
                            "total_lms_clicks": row.get("total_lms_clicks"),
                            "risk_status": data["risk_status"],
                            "dropout_probability": data["dropout_probability"],
                            "risk_label": data["risk_label"]
                        })
                except Exception as ex:
                    st.warning(f"Lỗi dự đoán dòng {index}: {ex}")
            
            # Lưu kết quả vào bộ nhớ session_state để không bị mất
            result_df = pd.DataFrame(risk_results)
            st.session_state["high_risk_df"] = result_df[result_df["risk_label"] == 1]
            st.session_state["total_len"] = len(result_df)
        
        # Hiển thị kết quả và nút gửi email (Đưa ra ngoài khối nút bấm để luôn hiển thị)
        if "high_risk_df" in st.session_state:
            high_risk_df = st.session_state["high_risk_df"]
            total_len = st.session_state.get("total_len", 0)
            
            st.markdown("---")
            st.subheader("📊 Kết quả tổng hợp phân tích toàn trường:")
            st.warning(f"⚠️ Hệ thống đã quét xong! Phát hiện **{len(high_risk_df)}** sinh viên có nguy cơ rớt môn cao trên tổng số {total_len} sinh viên.")
            
            # Hiển thị bảng danh sách sinh viên rủi ro
            st.dataframe(high_risk_df[["email", "studied_credits", "total_lms_clicks", "dropout_probability"]])
            
            # Nút bấm kích hoạt n8n gửi email hàng loạt
            if st.button("📧 Kích hoạt n8n gửi Email tự động cho toàn bộ danh sách rủi ro"):
                webhook_url = "http://localhost:5678/webhook/88704c7c-2610-4a25-9a94-600f1edc1d28" 
                sent_count = 0
                error_count = 0
                
                for _, r_row in high_risk_df.iterrows():
                    batch_payload = {
                        "email": r_row["email"],
                        "risk_prob": r_row["dropout_probability"],
                        "message": f"Hệ thống AI nhà trường cảnh báo bạn có tỷ lệ rủi ro rớt môn là {r_row['dropout_probability']}. Vui lòng gặp cố vấn học tập!"
                    }
                    try:
                        resp = requests.post(webhook_url, json=batch_payload, timeout=5)
                        if resp.status_code == 200:
                            sent_count += 1
                        else:
                            error_count += 1
                            st.error(f"❌ Gửi thất bại tới {r_row['email']} (Mã lỗi n8n: {resp.status_code})")
                    except Exception as ex:
                        error_count += 1
                        st.error(f"❌ Lỗi kết nối n8n với {r_row['email']}: {ex}")
                        
                if sent_count > 0:
                    st.success(f"✅ Đã tự động gửi thành công {sent_count} email cảnh báo qua luồng n8n!")
                if error_count > 0:
                    st.error(f"⚠️ Có {error_count} email không gửi được. Hãy kiểm tra lại n8n.")