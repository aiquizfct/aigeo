# -*- coding: utf-8 -*-

"""
Tệp kịch bản Python này minh họa cách tích hợp và sử dụng mô hình Gemini
thông qua API của Google AI.

Hướng dẫn:
1. Cài đặt hoặc cập nhật thư viện cần thiết:
   Mở terminal hoặc command prompt của bạn và chạy lệnh sau:
   pip install --upgrade google-generativeai

2. Lấy khóa API của bạn:
   - Truy cập Google AI Studio tại https://aistudio.google.com/
   - Nhấp vào "Get API key" và tạo một khóa API mới.

3. Chạy kịch bản:
   - Thay thế 'YOUR_API_KEY' trong kịch bản này bằng khóa API bạn vừa tạo.
   - Chạy tệp từ terminal: python gemini_flash_api.py
"""

import google.generativeai as genai
import os

def call_gemini():
    """
    Hàm này định cấu hình khóa API, khởi tạo mô hình Gemini,
    gửi một lời nhắc và in ra phản hồi.
    """
    try:
        # Định cấu hình khóa API của bạn.
        # Để bảo mật, tốt hơn là sử dụng biến môi trường.
        # Ví dụ: os.environ.get('GEMINI_API_KEY')
        api_key = 'AIzaSyC6tvEUmB3v8iMY4FHbWUibxq-eBSu5WZk' # <-- THAY THẾ BẰNG KHÓA API CỦA BẠN
        
        if api_key == 'YOUR_API_KEY' or not api_key:
            print("Lỗi: Vui lòng thay thế 'YOUR_API_KEY' bằng khóa API thực tế của bạn.")
            return

        genai.configure(api_key=api_key)

        # Khởi tạo mô hình. Chuyển sang 'gemini-pro' để kiểm tra.
        # Lỗi 404 thường xảy ra nếu thư viện của bạn quá cũ để hỗ trợ các mô hình mới hơn.
        # Hãy chắc chắn rằng bạn đã chạy 'pip install --upgrade google-generativeai'.
        model = genai.GenerativeModel('gemini-pro')

        # Lời nhắc (prompt) bạn muốn gửi đến mô hình.
        prompt = "Viết một bài thơ ngắn về Việt Nam."

        print(f"Đang gửi lời nhắc tới Gemini: '{prompt}'")
        
        # Gửi lời nhắc và nhận phản hồi
        response = model.generate_content(prompt)

        # In phản hồi văn bản từ mô hình
        print("\n--- Phản hồi từ Gemini ---")
        print(response.text)
        print("------------------------\n")

    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")
        print("Vui lòng kiểm tra lại khóa API và đảm bảo bạn đã cài đặt phiên bản mới nhất của thư viện 'google-generativeai'.")

if __name__ == "__main__":
    call_gemini()

