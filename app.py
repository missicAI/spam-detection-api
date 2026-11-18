from pathlib import Path

import joblib
import streamlit as st
from pydantic import ValidationError

from spamguard.service import PredictionRequest

ROOT = Path(__file__).resolve().parent
MODEL_PATH = ROOT / "artifacts/spam_model.joblib"
st.set_page_config(page_title="SpamGuard · SMS Classifier", page_icon="✉️", layout="wide")
st.title("✉️ SpamGuard — Phân loại tin nhắn")
st.caption("TF-IDF + Logistic Regression · Dữ liệu SMS tiếng Anh · API riêng bằng FastAPI")
if not MODEL_PATH.exists():
    st.info("Chạy python train.py trong thư mục dự án trước khi mở bản demo.")
    st.stop()


@st.cache_resource
def load_bundle(path, modified):
    return joblib.load(path)


bundle = load_bundle(str(MODEL_PATH), MODEL_PATH.stat().st_mtime_ns)
sample = st.selectbox("Thử nhanh", ["Tin thường", "Tin quảng cáo", "Tự nhập"])
defaults = {
    "Tin thường": "Hi, are we still meeting for lunch tomorrow?",
    "Tin quảng cáo": "Congratulations! You won a free prize. Call now to claim your cash reward!",
    "Tự nhập": "",
}
text = st.text_area("Tin nhắn tiếng Anh", defaults[sample], key=sample, height=150)
if st.button("Phân loại", type="primary"):
    try:
        payload = PredictionRequest(text=text)
        model = bundle["pipeline"]
        index = list(model.classes_).index("spam")
        probability = float(model.predict_proba([payload.text])[0, index])
        label = model.predict([payload.text])[0]
        st.subheader("🚩 Spam" if label == "spam" else "✅ Tin nhắn thường")
        st.metric("Xác suất spam do mô hình ước lượng", f"{probability:.1%}")
        st.caption("Đây là điểm của mô hình chưa hiệu chỉnh xác suất; không đảm bảo độ tin cậy tương ứng.")
    except ValidationError as exc:
        st.error(str(exc))
metrics = bundle["metadata"]["metrics"]
with st.expander("Kết quả trên tập kiểm tra"):
    st.json(metrics)
    st.caption(bundle["metadata"]["limitations"])
