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
    /* Tổng thể Dark Theme */
    .stApp { background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%); color: #e2e8f0; }
    /* Bong bóng chat tinh tế hơn */
    [data-testid="stChatMessage"] {
        border-radius: 20px;
        margin-bottom: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    /* Sidebar hiện đại */
    [data-testid="stSidebar"] {
        background-color: #0f172a;
        border-right: 1px dotted #334155;
    }
    /* Thanh cuộn (Scrollbar) đẹp hơn */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #0f172a; }
    ::-webkit-scrollbar-thumb { background: #334155; border-radius: 10px; }
    
    /* Hiệu ứng Glow cho tiêu đề */
    .glow-text {
        text-shadow: 0 0 10px #38bdf8, 0 0 20px #38bdf8;
        color: #f8fafc;
        font-weight: bold;
    }
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
    st.markdown("<h1 class='glow-text'>💎 GEMINI PRO</h1>", unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=80)
    
    with st.expander("📊 Trạng thái hệ thống", expanded=True):
        st.write(f"📅 Ngày: {datetime.datetime.now().strftime('%d/%m/%Y')}")
        st.write("📶 Kết nối: **Tốt**")
        st.progress(85, text="Tài nguyên API")  
    st.markdown("---")
    if st.button("➕ Cuộc trò chuyện mới", use_container_width=True):
        if st.session_state.messages:
            # Lưu lại cuộc trò chuyện cũ trước khi reset
            first_q = st.session_state.messages[0]["content"]
            title = (first_q[:25] + "...") if len(first_q) > 25 else first_q
            st.session_state.all_chats[title] = st.session_state.messages    
        st.session_state.messages = []
        st.rerun()

# --- ĐOẠN THÊM MỚI: NÚT XÓA TẤT CẢ ---
    if st.button("🗑️ Xóa tất cả lịch sử", use_container_width=True, type="secondary"):
        st.session_state.all_chats = {} # Xóa danh sách lưu trữ
        st.session_state.messages = []  # Xóa cuộc hội thoại hiện tại
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
# ---  TẠO HÀM XỬ LÝ PHẢN HỒI  ---
def thuc_thi_chat(cau_hoi):
    # Thêm câu hỏi của user vào session
    st.session_state.messages.append({"role": "user", "content": cau_hoi})
    # Kích hoạt việc chạy AI (sẽ được xử lý ở phần dưới)
    st.session_state.do_chat = True











# --- 5. HIỂN THỊ CÁC TIN NHẮN CŨ ---
for message in st.session_state.messages:
    avatar = "🧑‍💻" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# ---  GỢI Ý CÂU HỎI ---
if not st.session_state.messages:
    st.markdown("### Tôi có thể giúp gì cho bạn?")
    cols = st.columns(2)
    suggestions = ["💡 Giải thích AI", "📝 Viết email xin nghỉ", "✈️ Tour Đà Lạt", "💻 Code Python"]
    
    for i, suggestion in enumerate(suggestions):
        with cols[i % 2]:
            # KHI BẤM NÚT: Gán giá trị vào một biến tạm để xử lý ở bước kế tiếp
            if st.button(suggestion, use_container_width=True):
                st.session_state.prompt_tam = suggestion 
                st.rerun()





# --- 6. XỬ LÝ CÂU HỎI TỪ NGƯỜI DÙNG ---

# Lấy câu hỏi từ ô nhập liệu
prompt = st.chat_input("Bạn muốn hỏi gì thế?")

# KIỂM TRA: Nếu người dùng vừa bấm nút gợi ý (có prompt_tam)
if st.session_state.get("prompt_tam"):
    prompt = st.session_state.prompt_tam  # Gán nội dung nút bấm vào prompt
    del st.session_state.prompt_tam      # Xóa biến tạm để không bị lặp lại

# Nếu có prompt (từ bất kỳ nguồn nào) thì bắt đầu xử lý
if prompt:
    # Thêm và hiển thị tin nhắn người dùng
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)

    # Gửi đến Gemini và nhận phản hồi
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Đang suy nghĩ..."):
            try:
                # Chuyển đổi lịch sử chat
                history_data = [
                    {"role": "model" if m["role"] == "assistant" else "user", "parts": [m["content"]]}
                    for m in st.session_state.messages[:-1]
                ]
                
                chat_session = model.start_chat(history=history_data)
                response = chat_session.send_message(prompt)
                
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                
            except Exception as e:
                st.error(f"Lỗi: {e}")