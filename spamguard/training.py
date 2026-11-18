import csv
import hashlib
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.dummy import DummyClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from spamguard.download import DATA_PATH, ROOT, ensure_data


def clean_data(frame: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    raw_rows = len(frame)
    data = frame.dropna(subset=["label", "text"]).copy()
    data["text"] = data.text.astype(str).str.strip()
    data = data[data.label.isin(["ham", "spam"]) & data.text.ne("")].copy()
    valid_rows = len(data)
    data["key"] = data.text.str.replace(r"\s+", " ", regex=True).str.casefold()
    counts = data.groupby("key").label.nunique()
    conflicts = set(counts[counts > 1].index)
    conflict_rows = int(data.key.isin(conflicts).sum())
    data = data[~data.key.isin(conflicts)]
    deduped = data.drop_duplicates("key").reset_index(drop=True)
    return deduped, {
        "raw_rows": raw_rows,
        "invalid_rows_removed": raw_rows - valid_rows,
        "conflicting_rows_removed": conflict_rows,
        "duplicate_rows_removed": len(data) - len(deduped),
        "clean_rows": len(deduped),
    }


def make_pipeline() -> Pipeline:
    return Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    strip_accents="unicode",
                    ngram_range=(1, 2),
                    min_df=2,
                    max_features=20000,
                    sublinear_tf=True,
                ),
            ),
            ("classifier", LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)),
        ]
    )


def train(
    data_path: Path = DATA_PATH, output_dir: Path = ROOT / "artifacts", report_dir: Path = ROOT / "reports"
) -> dict:
    if not data_path.exists():
        if data_path != DATA_PATH:
            raise FileNotFoundError(data_path)
        ensure_data()
    raw = pd.read_csv(
        data_path, sep="\t", header=None, names=["label", "text"], quoting=csv.QUOTE_NONE, encoding="utf-8"
    )
    data, cleaning = clean_data(raw)
    if data.label.nunique() != 2 or data.label.value_counts().min() < 5:
        raise ValueError("Cần ít nhất 5 tin mỗi lớp sau khi làm sạch.")
    train_df, test_df = train_test_split(data, test_size=0.2, stratify=data.label, random_state=42)
    assert not set(train_df.key) & set(test_df.key)
    pipeline = make_pipeline()
    pipeline.fit(train_df.text, train_df.label)
    predictions = pipeline.predict(test_df.text)
    spam_index = list(pipeline.classes_).index("spam")
    probabilities = pipeline.predict_proba(test_df.text)[:, spam_index]
    precision, recall, f1, _ = precision_recall_fscore_support(
        test_df.label, predictions, average="binary", pos_label="spam", zero_division=0
    )
    baseline = DummyClassifier(strategy="most_frequent")
    baseline.fit(np.zeros((len(train_df), 1)), train_df.label)
    baseline_predictions = baseline.predict(np.zeros((len(test_df), 1)))
    _, _, baseline_f1, _ = precision_recall_fscore_support(
        test_df.label, baseline_predictions, average="binary", pos_label="spam", zero_division=0
    )
    report = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "dataset": "UCI SMS Spam Collection (English SMS)",
        "dataset_sha256": hashlib.sha256(data_path.read_bytes()).hexdigest(),
        "cleaning": cleaning,
        "split": {
            "train": len(train_df),
            "test": len(test_df),
            "test_fraction": 0.2,
            "stratified": True,
            "random_state": 42,
            "overlapping_normalized_messages": 0,
        },
        "test_class_counts": {str(k): int(v) for k, v in test_df.label.value_counts().items()},
        "metrics": {
            "accuracy": float(accuracy_score(test_df.label, predictions)),
            "spam_precision": float(precision),
            "spam_recall": float(recall),
            "spam_f1": float(f1),
            "roc_auc": float(roc_auc_score(test_df.label.eq("spam"), probabilities)),
        },
        "baseline": {
            "strategy": "always predict majority class",
            "accuracy": float(accuracy_score(test_df.label, baseline_predictions)),
            "spam_f1": float(baseline_f1),
        },
        "confusion_matrix": {
            "labels": ["ham", "spam"],
            "rows": "actual",
            "columns": "predicted",
            "values": confusion_matrix(test_df.label, predictions, labels=["ham", "spam"]).tolist(),
        },
        "versions": {
            "python": platform.python_version(),
            "scikit_learn": sklearn.__version__,
            "pandas": pd.__version__,
            "numpy": np.__version__,
        },
        "limitations": "Single random holdout from an old English SMS corpus; near-duplicates may remain. Not validated for Vietnamese, email, or current production traffic. Probabilities are not calibrated. No hyperparameter selection was performed on the test set.",
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    bundle = {"pipeline": pipeline, "metadata": report}
    joblib.dump(bundle, output_dir / "spam_model.joblib")
    (report_dir / "metrics.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    errors = test_df.loc[test_df.label.to_numpy() != predictions, ["label", "text"]].copy()
    errors["predicted"] = predictions[test_df.label.to_numpy() != predictions]
    errors.to_csv(report_dir / "misclassified.csv", index=False)
    return report
