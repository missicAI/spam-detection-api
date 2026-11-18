import pickle
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent


@lru_cache(maxsize=1)
def load_model():
    try:
        with (ROOT / "pkl/model_viet.pkl").open("rb") as handle:
            model = pickle.load(handle)
        with (ROOT / "pkl/vectorizer_viet.pkl").open("rb") as handle:
            vectorizer = pickle.load(handle)
    except FileNotFoundError:
        raise RuntimeError("Chưa có mô hình tiếng Việt. Chạy python train.py trước nhé.") from None
    return model, vectorizer


def predict(text):
    if not text.strip():
        raise ValueError("Bạn chưa nhập nội dung cần kiểm tra.")
    if len(text) > 5000:
        raise ValueError("Nội dung tối đa 5.000 ký tự.")
    model, vectorizer = load_model()
    input_vector = vectorizer.transform([text])
    return int(model.predict(input_vector)[0])
