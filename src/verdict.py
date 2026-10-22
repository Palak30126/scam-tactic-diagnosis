import html
from functools import lru_cache
from pathlib import Path

import joblib

from src.clean import scrub_pii
from src.tactics import ALL_TACTICS, TACTIC_LABELS, find_matches
from src.tagger import TacticTagger  # noqa: F401  (needed so joblib can load the saved tagger)

MODEL_DIR = Path(__file__).resolve().parents[1] / "models"


@lru_cache(maxsize=1)
def load_models():
    fake_path = MODEL_DIR / "fake_vs_real.joblib"
    tag_path = MODEL_DIR / "tactic_tagger.joblib"
    if not fake_path.exists() or not tag_path.exists():
        raise FileNotFoundError(
            "Models not found. Run: python -m src.baseline  and  python -m src.tagger"
        )
    return joblib.load(fake_path), joblib.load(tag_path)


def diagnose(raw_text: str, threshold: float = 0.5) -> dict:
    fake_bundle, tagger = load_models()
    cleaned = scrub_pii(raw_text)

    p_fake = fake_bundle["clf"].predict_proba(fake_bundle["vec"].transform([cleaned]))[0, 1]

    ml_probs = tagger.predict_proba([cleaned])[0]
    ml_tactics = {t for t, p in zip(ALL_TACTICS, ml_probs) if p >= 0.5}

    rule_hits = find_matches(raw_text)          # rules run on raw text so highlights line up
    tactics = sorted(ml_tactics | set(rule_hits))

    verdict = "FAKE" if (p_fake >= threshold or len(tactics) >= 2) else "REAL"
    spans = [s for hit_spans in rule_hits.values() for s in hit_spans]

    return {
        "verdict": verdict,
        "p_fake": float(p_fake),
        "tactics": tactics,
        "labels": {t: TACTIC_LABELS[t] for t in tactics},
        "spans": spans,
    }


def highlight(raw_text: str, spans) -> str:
    """Wrap matched phrases in <mark> tags. Everything else is HTML-escaped."""
    out, pos = [], 0
    for start, end, _ in sorted(spans):
        if start < pos:          # skip overlapping matches
            continue
        out.append(html.escape(raw_text[pos:start]))
        out.append(f"<mark>{html.escape(raw_text[start:end])}</mark>")
        pos = end
    out.append(html.escape(raw_text[pos:]))
    return "".join(out)