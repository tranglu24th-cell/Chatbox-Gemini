import streamlit as st
import google.generativeai as genai
import datetime
import time
import random

# --- 1. CẤU HÌNH TRANG WEB & GIAO DIỆN (GIỮ NGUYÊN CSS GỐC) ---
st.set_page_config(page_title="Gemini AI Chatbot", page_icon="🤖")
st.title("Gemini AI Collaborator")
st.caption("Một sản phẩm đồ án chạy bằng Python & Google Gemini")

st.markdown("""
<style>
    .stApp { background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%); color: #e2e8f0; }
    [data-testid="stChatMessage"] { border-radius: 20px; margin-bottom: 15px; border: 1px solid rgba(255, 255, 255, 0.1); box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
    [data-testid="stSidebar"] { background-color: #0f172a; border-right: 1px dotted #334155; }
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #0f172a; }
    ::-webkit-scrollbar-thumb { background: #334155; border-radius: 10px; }
    .glow-text { text-shadow: 0 0 10px #38bdf8, 0 0 20px #38bdf8; color: #f8fafc; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 2. KHỞI TẠO SESSION STATE ---
if "all_chats" not in st.session_state: st.session_state.all_chats = {} 
if "messages" not in st.session_state: st.session_state.messages = []

# --- 3. CẤU HÌNH API KEYS (LOAD BALANCING) ---
# Đoạn này sẽ tự gom KEY1, KEY2, KEY3... vào một danh sách
api_keys = [v for k, v in st.secrets.items() if "KEY" in k.upper()]
if not api_keys:
    st.error("⚠️ Chưa tìm thấy API Key trong Secrets.")
    st.stop()

# --- 4. HÀM CACHE KHỞI TẠO MODEL (CHỐNG LỖI 429 & 404) ---
@st.cache_resource
def get_gemini_model(api_key):
    try:
        genai.configure(api_key=api_key)
        # Quét model khả dụng để né lỗi 404
        available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        selected = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in available else available[0]
        
        today = datetime.datetime.now().strftime("%d/%m/%Y")
        instruction = f"Bạn là một cộng tác viên AI hữu ích. Hôm nay là ngày {today}."
        return genai.GenerativeModel(model_name=selected, system_instruction=instruction)
    except:
        return None

# --- 5. THANH SIDEBAR (ĐẦY ĐỦ TÍNH NĂNG CŨ) ---
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
            first_q = st.session_state.messages[0]["content"]
            title = (first_q[:25] + "...") if len(first_q) > 25 else first_q
            st.session_state.all_chats[title] = st.session_state.messages 
        st.session_state.messages = []
        st.rerun()

    if st.button("🗑️ Xóa tất cả lịch sử", use_container_width=True, type="secondary"):
        st.session_state.all_chats = {}
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.subheader("📝 Lịch sử trò chuyện")
    for title in list(st.session_state.all_chats.keys()):
        if st.sidebar.button(f"• {title}", key=title, use_container_width=True):
            st.session_state.messages = st.session_state.all_chats[title]
            st.rerun()

# --- 6. HIỂN THỊ CHAT ---
for message in st.session_state.messages:
    avatar = "🧑‍💻" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Gợi ý câu hỏi (Chỉ hiện khi chưa có tin nhắn)
if not st.session_state.messages:
    st.markdown("### Tôi có thể giúp gì cho bạn?")
    cols = st.columns(2)
    suggestions = ["💡 Giải thích AI", "📝 Viết email xin nghỉ", "✈️ Tour Đà Lạt", "💻 Code Python"]
    for i, suggestion in enumerate(suggestions):
        with cols[i % 2]:
            if st.button(suggestion, use_container_width=True):
                st.session_state.prompt_tam = suggestion 
                st.rerun()

# --- 7. XỬ LÝ CHAT (PHIÊN BẢN ĐÃ FIX LỖI 403 & 429) ---
prompt = st.chat_input("Bạn muốn hỏi gì thế?")

if st.session_state.get("prompt_tam"):
    prompt = st.session_state.prompt_tam
    del st.session_state.prompt_tam

if prompt:
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)
    
    with st.chat_message("assistant", avatar="🤖"):
        placeholder = st.empty()
        with st.spinner("Hệ thống đang kiểm tra API xịn cho bạn..."):
            success = False
            # Trộn danh sách Key
            shuffled_keys = list(api_keys)
            random.shuffle(shuffled_keys)
            
            # VÒNG LẬP THỬ TỪNG KEY
            for key in shuffled_keys:
                if success: break
                
                model = get_gemini_model(key)
                if not model: continue
                
                try:
                    # Lấy lịch sử hội thoại
                    context_limit = 5 
                    history = [{"role": "model" if m["role"] == "assistant" else "user", "parts": [m["content"]]} 
                               for m in st.session_state.messages[-context_limit:]]
                    
                    # Gửi tin nhắn
                    chat_session = model.start_chat(history=history)
                    response = chat_session.send_message(prompt)
                    
                    # Nếu chạy đến đây là THÀNH CÔNG
                    placeholder.markdown(response.text)
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                    success = True
                    break # Thoát vòng lặp key vì đã xong
                    
                except Exception as e:
                    # NẾU DÍNH LỖI 403 (Key hỏng) HOẶC 429 (Quá tải)
                    if "403" in str(e) or "429" in str(e):
                        # Không hiện lỗi lên màn hình, âm thầm đổi sang Key tiếp theo
                        continue 
                    else:
                        # Nếu là lỗi khác (như mất mạng) thì mới hiện
                        placeholder.error(f"Lỗi hệ thống: {e}")
                        success = True # Dừng lại không thử Key khác nữa
                        break
            
            # Nếu chạy hết danh sách Key mà vẫn không thành công
            if not success:
                placeholder.error("⚠️ Toàn bộ các API Keys đang bận hoặc bị lỗi. Bạn đợi 10 giây rồi thử lại nhé!")