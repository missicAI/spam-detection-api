# SpamGuard — Kiểm tra tin nhắn tiếng Việt

Ứng dụng giúp thử phân biệt tin nhắn thường và tin nhắn có dấu hiệu là tin rác. Bạn có thể dán nội dung tiếng Việt, thử một ví dụ hoặc gửi yêu cầu qua API.

Bản này được chỉnh từ dự án có sẵn của [DevWaqarAhmad](https://github.com/DevWaqarAhmad/Spam-SMS-Email-Classifier). Giao diện đã được Việt hóa và mô hình được học lại bằng dữ liệu SMS tiếng Việt gốc. Các ví dụ như báo trúng thưởng, yêu cầu nộp phí nhận quà và mời vay tiền được viết bằng tiếng Việt để dùng thử.

## Chạy trên máy

Cài Python 3.12. Trên Windows, mở `CAI_DAT.bat` một lần rồi chạy `CHAY_DEMO.bat`. Lần đầu cần mạng để tải dữ liệu và tạo mô hình; các lần sau có thể dùng lại mô hình đã lưu.

Nếu dùng terminal trong thư mục dự án:

```bash
python -m pip install -r requirements.txt
python train.py
python -m streamlit run app.py
```

Hai tệp có tên `model_viet.pkl` và `vectorizer_viet.pkl` được tạo trong thư mục `pkl`. Chúng là mô hình tiếng Việt; bản này không dùng lại mô hình tiếng Anh cũ.

## Đọc code

`train.py` tải dữ liệu, lọc các tin trùng, biến nội dung thành số rồi huấn luyện mô hình. Phần này dùng TF-IDF và Logistic Regression như dự án gốc. Đã bỏ cách xử lý chỉ giữ chữ cái tiếng Anh để không làm mất chữ có dấu.

`du_doan.py` dùng mô hình đã lưu để kiểm tra tin mới. `app.py` là phần giao diện. Nếu muốn xem những tin mô hình đoán sai, mở `reports/cac_tin_doan_sai.csv` sau khi huấn luyện.

Để mở API:

```bash
python -m uvicorn api:app --host 127.0.0.1 --port 8000
```

Vào http://127.0.0.1:8000/docs, chọn `/predict` và gửi nội dung theo mẫu:

```json
{"noi_dung": "Chúc mừng bạn đã trúng thưởng. Hãy nộp phí để nhận quà."}
```

## Kết quả có thể nhầm

Mô hình học từ bộ SMS công khai, thiên về thông báo dịch vụ và tin rác/lừa đảo. Câu trò chuyện ngắn, email dài hoặc kiểu quảng cáo chưa gặp có thể bị đoán sai. Không nên dùng kết quả này để tự động chặn tin quan trọng hoặc kết luận một người gửi là lừa đảo.

Một từ như “trúng thưởng” không quyết định kết quả của mọi tin. Hãy thử cả câu có lời mời nhận thưởng và câu nhắc người thân cảnh giác để quan sát khác biệt.

Điểm đo được lưu trong `reports/ket_qua.json`. Bộ kiểm tra đã được dùng khi phát triển bản tiếng Việt, không phải kiểm định độc lập. Đã loại bản trùng nguyên văn sau chuẩn hóa; các tin gần giống nhau vẫn có thể còn.

Ở lần chạy được lưu trong dự án, mô hình đoán đúng 518 trong 564 tin kiểm tra và còn 46 tin đoán sai. Những con số này không có nghĩa nó sẽ đạt kết quả tương tự với mọi tin nhắn bạn nhập.

Chạy kiểm tra code bằng:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Nguồn code, dữ liệu và các phần đã chỉnh được ghi tại [NGUON.md](NGUON.md). Giữ giấy phép MIT của tác giả code; dữ liệu tiếng Việt dùng giấy phép CC BY 4.0.
