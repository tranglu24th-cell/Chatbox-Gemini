import streamlit as st
import google.generativeai as genai

# 1. Cấu hình trang web
st.set_page_config(page_title="Gemini AI Chatbot", page_icon="🤖")
st.title("💬 Gemini AI Collaborator")
st.caption("🚀 Một sản phẩm đồ án chạy bằng Python & Google Gemini")

# 2. Cấu hình API Key (Thay bằng Key của bạn)

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Chưa cấu hình API Key trong phần Secrets của Streamlit!")
model = genai.GenerativeModel('gemini-2.5-flash')

# 3. Khởi tạo lịch sử chat nếu chưa có
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. Hiển thị các tin nhắn cũ từ lịch sử
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Xử lý câu hỏi từ người dùng
if prompt := st.chat_input("Bạn muốn hỏi gì thế?"):
    # Hiển thị tin nhắn người dùng
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Gửi đến Gemini và nhận phản hồi
    with st.chat_message("assistant"):
        with st.spinner("Đang suy nghĩ..."):
            try:
                # Gửi toàn bộ lịch sử để AI có "ngữ cảnh"
                full_chat = model.start_chat(history=[
                    {"role": m["role"] == "assistant" and "model" or "user", "parts": [m["content"]]}
                    for m in st.session_state.messages[:-1]
                ])
                response = full_chat.send_message(prompt)
                
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Lỗi rồi: {e}")