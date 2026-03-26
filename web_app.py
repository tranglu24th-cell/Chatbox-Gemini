import streamlit as st
import google.generativeai as genai
import datetime

# --- 1. CẤU HÌNH TRANG WEB & GIAO DIỆN ---
st.set_page_config(page_title="Gemini AI Chatbot", page_icon="🤖")
st.title("Gemini AI Collaborator")
st.caption("Một sản phẩm đồ án chạy bằng Python & Google Gemini")

# Chèn CSS để làm đẹp giao diện tối (Dark Mode)
st.markdown("""
<style>
    .stApp { background-color: #1a1a1a; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #111111; border-right: 1px solid #333333; }
    .stChatInputContainer { background-color: #262626; }
</style>
""", unsafe_allow_html=True)

# --- 2. KHỞI TẠO LỊCH SỬ CHAT (SESSION STATE) ---
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {} 
if "messages" not in st.session_state:
    st.session_state.messages = []
if "past_chats" not in st.session_state:
    st.session_state.past_chats = [] 

# --- 3. THANH SIDEBAR (QUẢN LÝ LỊCH SỬ) ---
with st.sidebar:
    st.title("🤖 Gemini AI")
    
    if st.button("➕ Cuộc trò chuyện mới", use_container_width=True):
        if st.session_state.messages:
            # Lưu lại cuộc trò chuyện cũ trước khi reset
            first_q = st.session_state.messages[0]["content"]
            title = (first_q[:25] + "...") if len(first_q) > 25 else first_q
            st.session_state.all_chats[title] = st.session_state.messages
            
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.subheader("📝 Lịch sử trò chuyện")
    
    for title in st.session_state.all_chats.keys():
        if st.sidebar.button(f"• {title}", key=title, use_container_width=True):
            st.session_state.messages = st.session_state.all_chats[title]
            st.rerun()

# --- 4. CẤU HÌNH API KEY & KHỞI TẠO MODEL ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.warning("⚠️ Chưa tìm thấy API Key trong Secrets.")
    st.stop()

# Khởi tạo model DUY NHẤT một lần với System Instruction
try:
    today = datetime.datetime.now().strftime("%d/%m/%Y")
    # Lời dặn giúp AI biết ngày tháng mà không nhắc thừa thãi
    instruction = f"Bạn là một cộng tác viên AI hữu ích. Hôm nay là ngày {today}. Chỉ nhắc đến ngày tháng nếu người dùng hỏi."

    # Tự động chọn model ổn định nhất (Ưu tiên gemini-1.5-flash)
    models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    selected_model = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in models else models[0]
    
    model = genai.GenerativeModel(
        model_name=selected_model,
        system_instruction=instruction
    )
except Exception as e:
    st.error(f"Lỗi khởi tạo AI: {e}")
    st.stop()

# --- 5. HIỂN THỊ CÁC TIN NHẮN CŨ ---
for message in st.session_state.messages:
    avatar = "🧑‍💻" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# --- 6. XỬ LÝ CÂU HỎI TỪ NGƯỜI DÙNG ---
if prompt := st.chat_input("Bạn muốn hỏi gì thế?"):
    # Hiển thị tin nhắn người dùng
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)

    # Gửi đến Gemini và nhận phản hồi
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Đang suy nghĩ..."):
            try:
                # Chuyển đổi lịch sử chat sang định dạng của Google AI
                history_data = [
                    {"role": "model" if m["role"] == "assistant" else "user", "parts": [m["content"]]}
                    for m in st.session_state.messages[:-1]
                ]
                
                chat_session = model.start_chat(history=history_data)
                response = chat_session.send_message(prompt)
                
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                
            except Exception as e:
                if "429" in str(e):
                    st.error("⚠️ Bạn hỏi nhanh quá! Đợi 1 phút để Google hồi phục lượt dùng nhé.")
                elif "403" in str(e):
                    st.error("🚫 API Key không hợp lệ hoặc bị khóa.")
                else:
                    st.error(f"❌ Lỗi hệ thống: {e}")