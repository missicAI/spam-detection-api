# Việt hóa và rút gọn app.py của DevWaqarAhmad; xem NGUON.md.
import streamlit as st

from du_doan import load_model, predict

st.set_page_config(page_title="SpamGuard — Kiểm tra tin nhắn", page_icon="✉️", layout="centered")
st.title("✉️ Kiểm tra tin nhắn rác")
st.write("Dán tin nhắn tiếng Việt vào bên dưới để kiểm tra. Bạn có thể thử một trong các ví dụ có sẵn.")

examples = {
    "Tự nhập": "",
    "Thông báo mã xác nhận": "Mã OTP đăng nhập của bạn là [NUMBER]. Không chia sẻ mã này với bất kỳ ai.",
    "Báo trúng thưởng": "Chúc mừng bạn đã trúng thưởng một chiếc iPhone. Chuyển khoản phí nhận quà để nhận thưởng ngay.",
    "Mời vay tiền": "Vay nhanh trong ngày, không cần thế chấp, lãi suất ưu đãi. Bấm vào đường dẫn để đăng ký nhận tiền.",
}
choice = st.selectbox("Chọn ví dụ", list(examples))
user_input = st.text_area(
    "Nội dung tin nhắn",
    examples[choice],
    height=170,
    placeholder="Nhập hoặc dán tin nhắn tiếng Việt ở đây…",
    key=choice,
)
try:
    load_model()
except RuntimeError as exc:
    st.info(str(exc))
    st.stop()

if st.button("Kiểm tra tin nhắn", type="primary"):
    try:
        prediction = predict(user_input)
        if prediction == 1:
            st.warning("Tin nhắn có dấu hiệu là tin rác. Bạn nên đọc kỹ nội dung và đường dẫn đi kèm.")
        else:
            st.success("Chưa phát hiện dấu hiệu tin rác trong nội dung này.")
        st.caption(
            "Kết quả có thể nhầm. Chương trình không xác minh người gửi hoặc độ an toàn của đường dẫn."
        )
    except (ValueError, RuntimeError) as exc:
        st.error(str(exc))

with st.expander("Chương trình kiểm tra như thế nào?"):
    st.write(
        "Mô hình học từ các tin nhắn tiếng Việt đã có nhãn. Nó xem nội dung cả tin, thay vì chỉ dò một từ như ‘trúng thưởng’."
    )
    st.write("Bản đơn giản này vẫn có thể đoán sai, nhất là câu trò chuyện ngắn hoặc email dài.")
