import pandas as pd
from sklearn.metrics import cohen_kappa_score

from src.tactics import ALL_TACTICS


def load(path):
    return pd.read_csv(path).fillna("").set_index("id")


def tactic_series(df, tactic):
    return df["tactics"].astype(str).str.contains(tactic).astype(int)


def main():
    a = load("data/indian/agreement/annotator_A.csv")
    b = load("data/indian/agreement/annotator_B.csv")
    common = a.index.intersection(b.index)
    a, b = a.loc[common], b.loc[common]
    print(f"Posts compared: {len(common)}")

    print(f"Kappa, fake vs real: {cohen_kappa_score(a['fake'], b['fake']):.3f}")

    print("\nKappa per tactic:")
    for t in ALL_TACTICS:
        ta, tb = tactic_series(a, t), tactic_series(b, t)
        if ta.nunique() == 1 and tb.nunique() == 1 and ta.iloc[0] == tb.iloc[0]:
            print(f"{t:24s} n/a (no variation in these 30 posts)")
        else:
            print(f"{t:24s} {cohen_kappa_score(ta, tb):.3f}")


if __name__ == "__main__":
    main()