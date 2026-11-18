from pathlib import Path
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from streamlit.testing.v1 import AppTest

import du_doan
from api import app
from train import clean_data


@pytest.fixture
def model(monkeypatch):
    text = [
        "Mã xác nhận đăng nhập của bạn",
        "Mã xác nhận tài khoản không chia sẻ",
        "Trúng thưởng nhận quà nộp phí ngay",
        "Chúc mừng trúng thưởng chuyển phí nhận quà",
    ]
    vectorizer = TfidfVectorizer()
    classifier = LogisticRegression().fit(vectorizer.fit_transform(text), [0, 0, 1, 1])
    monkeypatch.setattr(du_doan, "load_model", lambda: (classifier, vectorizer))


def test_clean_data_keeps_vietnamese_and_removes_duplicates():
    frame = pd.DataFrame({"message": [" Trúng thưởng ", "trúng   thưởng", "Mã xác nhận"], "label": [1, 1, 0]})
    clean = clean_data(frame)
    assert len(clean) == 2
    assert "Trúng thưởng" in clean.message.tolist()


def test_conflicting_labels_are_removed():
    frame = pd.DataFrame({"message": ["cùng một tin", "CÙNG MỘT TIN", "mã xác nhận"], "label": [0, 1, 0]})
    assert clean_data(frame).message.tolist() == ["mã xác nhận"]


def test_predictions_accept_vietnamese(model):
    assert du_doan.predict("Mã xác nhận đăng nhập của bạn") == 0
    assert du_doan.predict("Trúng thưởng nhận quà nộp phí ngay") == 1


@pytest.mark.parametrize("text", [" ", "x" * 5001])
def test_invalid_input_is_rejected_in_vietnamese(text):
    with pytest.raises(ValueError):
        du_doan.predict(text)


def test_api_uses_vietnamese_fields(model):
    with TestClient(app) as client:
        result = client.post("/predict", json={"noi_dung": "Trúng thưởng nhận quà nộp phí ngay"})
        assert result.status_code == 200
        assert result.json() == {"nhan": 1, "ket_qua": "Có dấu hiệu tin rác"}
        assert client.post("/predict", json={"noi_dung": " "}).status_code == 422


def test_interface_accepts_vietnamese(model):
    at = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py", default_timeout=15).run()
    at.text_area[0].set_value("Trúng thưởng nhận quà nộp phí ngay")
    at.button[0].click().run()
    assert not at.exception
    assert "tin rác" in at.warning[0].value
