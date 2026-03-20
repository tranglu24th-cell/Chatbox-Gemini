import google.generativeai as genai

# Dán Key lấy từ AI Studio vào đây
genai.configure(api_key="AIzaSyClVM7p6Kb9xDY5m6aTgr_blhi4Dsk4MlU") 

# Workflow chuẩn: Sử dụng tên model không có tiền tố 'models/' nếu thư viện đã cũ
# Hoặc thử chính xác tên này:
model = genai.GenerativeModel('gemini-2.5-flash')

def chat():
    # Thầy bạn có thể dùng workflow 'generate_content' thay vì 'start_chat' để test nhanh
    response = model.generate_content("Xin chào, bạn là ai?")
    print(response.text)

if __name__ == "__main__":
    chat()