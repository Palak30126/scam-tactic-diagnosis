import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, classification_report, f1_score
from sklearn.model_selection import train_test_split

from src.clean import build_text


def main():
    df = pd.read_csv("data/raw/fake_job_postings.csv")
    df["text"] = build_text(df)

    X_tr, X_te, y_tr, y_te = train_test_split(
        df["text"], df["fraudulent"],
        test_size=0.2, stratify=df["fraudulent"], random_state=42,
    )

    vec = TfidfVectorizer(ngram_range=(1, 2), min_df=3,
                          max_features=50_000, stop_words="english")
    clf = LogisticRegression(max_iter=1000, class_weight="balanced")
    clf.fit(vec.fit_transform(X_tr), y_tr)

    proba = clf.predict_proba(vec.transform(X_te))[:, 1]

    print(f"PR-AUC (fake class): {average_precision_score(y_te, proba):.3f}")
    print(f"F1 (fake class):     {f1_score(y_te, proba >= 0.5):.3f}")
    print(classification_report(y_te, proba >= 0.5, digits=3))

    joblib.dump({"vec": vec, "clf": clf}, "models/fake_vs_real.joblib")
    print("Saved models/fake_vs_real.joblib")


if __name__ == "__main__":
    main()