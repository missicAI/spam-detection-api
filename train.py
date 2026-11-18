# Chuyển phần huấn luyện từ notebook của DevWaqarAhmad sang dữ liệu tiếng Việt; xem NGUON.md.
import json
import pickle
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support

ROOT = Path(__file__).resolve().parent
DATA_URL = "https://raw.githubusercontent.com/trannguyenthaituan251209/vietnamese_sms_dataset/464a028878023598e16f2f344ee36f7d5d74257f/"


def read_data(name):
    path = ROOT / "data" / name
    if not path.exists():
        path.parent.mkdir(exist_ok=True)
        try:
            data = pd.read_csv(DATA_URL + name)
        except Exception as exc:
            raise RuntimeError("Chưa tải được dữ liệu tiếng Việt. Hãy kiểm tra kết nối mạng.") from exc
        data.to_csv(path, index=False)
    return pd.read_csv(path).dropna(subset=["message", "label"])


def clean_data(data):
    data = data.copy()
    data["message"] = data.message.astype(str).str.strip()
    data = data[data.message.ne("") & data.label.isin([0, 1])].copy()
    data["key"] = data.message.str.casefold().str.replace(r"\s+", " ", regex=True)
    conflicts = data.groupby("key").label.nunique()
    data = data[~data.key.isin(conflicts[conflicts > 1].index)]
    return data.drop_duplicates("key").reset_index(drop=True)


def train():
    raw_train, raw_test = read_data("train.csv"), read_data("test.csv")
    train_data, test_data = clean_data(raw_train), clean_data(raw_test)
    overlap = train_data.key.isin(test_data.key)
    overlapping_rows = int(overlap.sum())
    train_data = train_data[~overlap]
    tfidf = TfidfVectorizer(max_features=5000)
    X_train = tfidf.fit_transform(train_data.message)
    X_test = tfidf.transform(test_data.message)
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, train_data.label)
    y_pred = model.predict(X_test)
    precision, recall, f1, _ = precision_recall_fscore_support(
        test_data.label, y_pred, average="binary", zero_division=0
    )
    report = {
        "ngon_ngu": "Tiếng Việt",
        "so_tin_goc": {"hoc": len(raw_train), "kiem_tra": len(raw_test)},
        "so_tin_da_loc": {"hoc": len(train_data), "kiem_tra": len(test_data)},
        "so_tin_hoc_trung_voi_tap_kiem_tra_da_bo": overlapping_rows,
        "ty_le_doan_dung": float(accuracy_score(test_data.label, y_pred)),
        "do_chinh_xac_khi_bao_tin_rac": float(precision),
        "ty_le_phat_hien_tin_rac": float(recall),
        "diem_f1_tin_rac": float(f1),
        "bang_ket_qua": confusion_matrix(test_data.label, y_pred, labels=[0, 1]).tolist(),
        "cach_doc_bang": "Hàng là nhãn thật, cột là nhãn dự đoán; 0: tin thường, 1: tin rác.",
        "pham_vi": "Bộ kiểm tra đã được dùng trong quá trình phát triển bản tiếng Việt; không phải kết quả kiểm định độc lập. Đã bỏ trùng nguyên văn sau chuẩn hóa; tin gần giống vẫn có thể còn. Dữ liệu thiên về SMS thông báo và rác/lừa đảo, chưa đại diện cho email dài hoặc hội thoại hằng ngày.",
    }
    (ROOT / "pkl").mkdir(exist_ok=True)
    for filename, value in [("model_viet.pkl", model), ("vectorizer_viet.pkl", tfidf)]:
        with (ROOT / "pkl" / filename).open("wb") as handle:
            pickle.dump(value, handle)
    output = ROOT / "reports"
    output.mkdir(exist_ok=True)
    (output / "ket_qua.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    errors = test_data.loc[test_data.label.to_numpy() != y_pred, ["message", "label"]].copy()
    errors["du_doan"] = y_pred[test_data.label.to_numpy() != y_pred]
    errors.to_csv(output / "cac_tin_doan_sai.csv", index=False)
    return report


if __name__ == "__main__":
    print(json.dumps(train(), ensure_ascii=False, indent=2))
