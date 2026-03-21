import streamlit as st
import google.generativeai as genai


# 3. Khởi tạo lịch sử chat nếu chưa có

# Khởi tạo kho lưu trữ tất cả các cuộc hội thoại cũ
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {}  # Lưu dưới dạng: { "Tiêu đề": [danh sách tin nhắn] }

# Khởi tạo cuộc hội thoại hiện tại
if "messages" not in st.session_state:
    st.session_state.messages = []

#if "messages" not in st.session_state:
    #st.session_state.messages = []

# 1. Cấu hình trang web
st.set_page_config(page_title="Gemini AI Chatbot", page_icon="🤖")
st.title("Gemini AI Collaborator")
st.caption("Một sản phẩm đồ án chạy bằng Python & Google Gemini")
#------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "past_chats" not in st.session_state:
    st.session_state.past_chats = [] 
#------------------------------
with st.sidebar:
    st.title("🤖 Gemini AI")
    
    # Nút tạo cuộc trò chuyện mới
    if st.button("➕ Cuộc trò chuyện mới", use_container_width=True):
        if st.session_state.messages:
            # Lấy câu hỏi đầu tiên làm tiêu đề để lưu
            first_question = st.session_state.messages[0]["content"]
            title = (first_question[:25] + "...") if len(first_question) > 25 else first_question
            
            # Lưu toàn bộ đoạn chat hiện tại vào kho
            st.session_state.all_chats[title] = st.session_state.messages
            
        # Reset để qua trang mới
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.subheader("📝 Lịch sử trò chuyện")
    
    # Hiển thị danh sách các cuộc trò chuyện đã lưu
    for title in st.session_state.all_chats.keys():
        if st.sidebar.button(f"• {title}", key=title, use_container_width=True):
            # Khi nhấn vào tiêu đề, tải lại toàn bộ tin nhắn của đoạn chat đó
            st.session_state.messages = st.session_state.all_chats[title]
            st.rerun()

    # Hiển thị tất cả lịch sử đã lưu ra Sidebar
    for chat_title in st.session_state.past_chats:
        st.write(f"• {chat_title}")
    #------------------------------
    

# Chèn vào dưới dòng st.caption
st.markdown("""
<style>
    .stApp { background-color: #1a1a1a; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #111111; border-right: 1px solid #333333; }
    .stChatInputContainer { background-color: #262626; }
</style>
""", unsafe_allow_html=True)



# 2. Cấu hình API Key 
# 2. Cấu hình API Key và Tự động chọn Model
# 2. Cấu hình API Key (Chỉ dùng secrets để bảo mật tuyệt đối)
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    # Nếu chạy local mà chưa có file secrets.toml thì hiện cảnh báo
    st.warning("⚠️ Chưa tìm thấy API Key. Nếu chạy local, hãy kiểm tra file secrets.toml")
    st.stop()



    
# Cách này giúp lấy đúng model đang hoạt động, tránh lỗi 404 (Not Found)
try:
    # Lấy danh sách các model mà API Key của bạn được phép dùng
    models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    # Ưu tiên chọn bản flash cho nhanh, nếu không có thì lấy bản đầu tiên trong danh sách
    selected_model = 'models/gemini-2.5-flash' if 'models/gemini-2.5-flash' in models else models[0]
    model = genai.GenerativeModel(selected_model)
except Exception as e:
    st.error(f"Lỗi kết nối API: {e}")

# 3. Khởi tạo lịch sử chat nếu chưa có
#if "messages" not in st.session_state:
    #st.session_state.messages = []

# 4. Hiển thị các tin nhắn cũ từ lịch sử
for message in st.session_state.messages:
    avatar = "🧑‍💻" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"],avatar=avatar):
        st.markdown(message["content"])




# 5. Xử lý câu hỏi từ người dùng
if prompt := st.chat_input("Bạn muốn hỏi gì thế?"):
    # Hiển thị tin nhắn người dùng
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user",avatar="🧑‍💻"):
        st.markdown(prompt)

    # Gửi đến Gemini và nhận phản hồi
    with st.chat_message("assistant", avatar="🤖"):
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