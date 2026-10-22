"""Tactic tagger: a TF-IDF plus one logistic regression per tactic, trained on the Indian set."""
import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split

from src.clean import scrub_pii
from src.tactics import ALL_TACTICS

MODEL_PATH = "models/tactic_tagger.joblib"


class TacticTagger:
    def __init__(self):
        self.vec = TfidfVectorizer(ngram_range=(1, 2), min_df=1, stop_words="english")
        self.models = {}
        self.constant = {}

    def fit(self, texts, Y: pd.DataFrame):
        X = self.vec.fit_transform(texts)
        self.models, self.constant = {}, {}
        for t in ALL_TACTICS:
            y = Y[t].to_numpy()
            if y.min() == y.max():          # only one class in the data for this tactic
                self.constant[t] = float(y[0])
            else:
                clf = LogisticRegression(max_iter=1000, class_weight="balanced")
                clf.fit(X, y)
                self.models[t] = clf
        return self

    def predict_proba(self, texts) -> np.ndarray:
        X = self.vec.transform(texts)
        out = np.zeros((X.shape[0], len(ALL_TACTICS)))
        for j, t in enumerate(ALL_TACTICS):
            if t in self.models:
                out[:, j] = self.models[t].predict_proba(X)[:, 1]
            else:
                out[:, j] = self.constant[t]
        return out


def load_posts():
    df = pd.read_csv("data/indian/posts.csv").fillna("")
    df["text"] = df["text"].apply(scrub_pii)
    df["tactic_list"] = df["tactics"].apply(
        lambda s: [x.strip() for x in str(s).split(";") if x.strip()]
    )
    unknown = {t for lst in df["tactic_list"] for t in lst} - set(ALL_TACTICS)
    if unknown:
        raise ValueError(f"Unknown tactic names in posts.csv: {unknown}")
    Y = pd.DataFrame({t: df["tactic_list"].apply(lambda l, t=t: int(t in l))
                      for t in ALL_TACTICS})
    return df, Y


def main():
    df, Y = load_posts()
    idx_tr, idx_te = train_test_split(df.index, test_size=0.25, random_state=42)

    tagger = TacticTagger().fit(df.loc[idx_tr, "text"], Y.loc[idx_tr])
    probs = tagger.predict_proba(df.loc[idx_te, "text"])
    pred = (probs >= 0.5).astype(int)
    truth = Y.loc[idx_te].to_numpy()

    print(f"Macro-F1 on held-out 25%: "
          f"{f1_score(truth, pred, average='macro', zero_division=0):.3f}")
    print(f"{'tactic':24s} precision  recall")
    for j, t in enumerate(ALL_TACTICS):
        p = precision_score(truth[:, j], pred[:, j], zero_division=0)
        r = recall_score(truth[:, j], pred[:, j], zero_division=0)
        print(f"{t:24s} {p:9.2f} {r:7.2f}")

    # Refit on all labelled data for the saved model
    final = TacticTagger().fit(df["text"], Y)
    joblib.dump(final, MODEL_PATH)
    print(f"Saved {MODEL_PATH}")


if __name__ == "__main__":
    # Import the module by its package name, so the saved class is src.tagger.TacticTagger
    from src.tagger import main as run
    run()