import pandas as pd

from spamguard.training import clean_data, make_pipeline


def test_cleaning_removes_duplicates_and_all_conflicting_labels():
    raw = pd.DataFrame(
        {
            "label": ["ham", "ham", "spam", "ham", "spam"],
            "text": ["Hello friend", "  hello   FRIEND ", "Conflict", "conflict", "Free prize"],
        }
    )
    clean, counts = clean_data(raw)
    assert len(clean) == 2
    assert counts["duplicate_rows_removed"] == 1
    assert counts["conflicting_rows_removed"] == 2


def test_test_only_words_never_enter_vocabulary():
    pipeline = make_pipeline()
    pipeline.fit(
        ["hello friend lunch", "hello friend meet", "free prize win", "free prize cash"],
        ["ham", "ham", "spam", "spam"],
    )
    pipeline.predict(["unseenholdouttoken"])
    assert "unseenholdouttoken" not in pipeline.named_steps["tfidf"].vocabulary_
    assert pipeline.predict(["hello friend"])[0] == "ham"
    assert pipeline.predict(["free prize"])[0] == "spam"
