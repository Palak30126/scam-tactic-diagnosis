import matplotlib
matplotlib.use("Agg")                     # save charts without opening a window
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, f1_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict, train_test_split
from sklearn.pipeline import make_pipeline

from src.clean import build_text, scrub_pii


def make_model():
    return make_pipeline(
        TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_features=50_000, stop_words="english"),
        LogisticRegression(max_iter=1000, class_weight="balanced"),
    )


def metrics(y, proba):
    return round(average_precision_score(y, proba), 3), round(f1_score(y, proba >= 0.5), 3)


def main():
    emscad = pd.read_csv("data/raw/fake_job_postings.csv")
    emscad["text"] = build_text(emscad)

    indian = pd.read_csv("data/indian/posts.csv").fillna("")
    indian["text"] = indian["text"].apply(scrub_pii)

    e_tr, e_te = train_test_split(
        emscad, test_size=0.2, stratify=emscad["fraudulent"], random_state=42)

    model = make_model().fit(e_tr["text"], e_tr["fraudulent"])

    rows = []
    rows.append(("Train EMSCAD, test EMSCAD",
                 *metrics(e_te["fraudulent"], model.predict_proba(e_te["text"])[:, 1])))
    rows.append(("Train EMSCAD, test Indian",
                 *metrics(indian["fake"], model.predict_proba(indian["text"])[:, 1])))

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_proba = cross_val_predict(make_model(), indian["text"], indian["fake"],
                                 cv=skf, method="predict_proba")[:, 1]
    rows.append(("Train Indian, test Indian (5-fold CV)",
                 *metrics(indian["fake"], cv_proba)))

    table = pd.DataFrame(rows, columns=["Setup", "PR-AUC", "F1 (fake)"])
    print(table.to_markdown(index=False))
    table.to_csv("reports/cross_dataset_results.csv", index=False)

    ax = table.set_index("Setup")[["PR-AUC", "F1 (fake)"]].plot(kind="bar", figsize=(9, 5))
    ax.set_ylim(0, 1)
    ax.set_title("Fake-job detection: in-domain vs cross-dataset")
    plt.xticks(rotation=15, ha="right")
    plt.tight_layout()
    plt.savefig("reports/cross_dataset_chart.png", dpi=150)
    print("Saved reports/cross_dataset_results.csv and reports/cross_dataset_chart.png")


if __name__ == "__main__":
    main()