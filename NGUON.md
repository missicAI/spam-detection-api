# Nguồn dự án

Phần giao diện và cách huấn luyện được chỉnh từ [Spam-SMS-Email-Classifier của DevWaqarAhmad](https://github.com/DevWaqarAhmad/Spam-SMS-Email-Classifier), bản `c97f518cd53798a4fd73a0c5474aee8b053ffcfd`. Giữ nguyên giấy phép MIT của tác giả.

Các phần dùng lại là `app.py` và các bước TF-IDF, Logistic Regression, lưu mô hình trong `spam_classifier.ipynb`.

Bản tiếng Việt bỏ cách xử lý chỉ dành cho chữ tiếng Anh, dùng CSV tiếng Việt thay cho bộ SMS tiếng Anh, tách dữ liệu trước khi học và loại tin trùng giữa hai tập. Không dùng lại mô hình tiếng Anh đã lưu sẵn. Phần huấn luyện được đưa thành `train.py` để chạy trực tiếp. Giao diện được Việt hóa, bỏ trang trí và thêm ví dụ tiếng Việt tự soạn để dùng thử. API là phần nối thêm, nằm riêng trong `api.py`.

Dữ liệu: [Vietnamese SMS Dataset](https://github.com/trannguyenthaituan251209/vietnamese_sms_dataset), bản `464a028878023598e16f2f344ee36f7d5d74257f`, giấy phép [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

Nhóm dữ liệu: Trần Nguyễn Thái Tuấn, Lê Hoàng Khang, Nguyễn Minh Tài, Nguyễn Văn Thắng và Mai Hoàng Đỉnh. Theo giới thiệu của nhóm, đây là SMS tiếng Việt được thu thập từ thực tế, không phải dữ liệu dịch từ tiếng Anh. Chương trình tải hai tệp `train.csv` và `test.csv` gốc rồi lọc trùng khi huấn luyện; không sửa nhãn hoặc dịch nội dung.

Ví dụ ở giao diện là câu dùng thử được viết bằng tiếng Việt, không nằm trong dữ liệu học. Điểm số trong `reports/ket_qua.json` là kết quả chạy của bản chỉnh này, không lấy từ README của tác giả.
