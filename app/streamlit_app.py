import sys
from pathlib import Path

# Make the project root importable so "from src..." works when Streamlit runs this file
sys.path.append(str(Path(__file__).resolve().parents[1]))

import streamlit as st

from src.verdict import diagnose, highlight

EXAMPLE = (
    "Earn ₹50,000 per week from home. Instant selection, no interview needed. "
    "Pay a registration fee of ₹999 to confirm your seat. Contact HR on WhatsApp "
    "only at +91 98765 43210. Apply today, limited seats!"
)

st.set_page_config(page_title="Scam Tactic Diagnosis", page_icon="🔎", layout="centered")
st.title("Scam Tactic Diagnosis")
st.caption("Paste a job or internship posting. The app returns a verdict, the scam tactics "
           "it found, and the phrases behind each one.")

# The example button must come before the text area, so session_state can be set safely
if st.button("Load example"):
    st.session_state["posting"] = EXAMPLE

text = st.text_area("Posting text", height=250, key="posting")

if st.button("Analyse", type="primary"):
    if not text.strip():
        st.warning("Paste a posting first.")
    else:
        try:
            r = diagnose(text)
        except FileNotFoundError as e:
            st.error(str(e))
            st.stop()

        col1, col2 = st.columns(2)
        col1.metric("Verdict", r["verdict"])
        col2.metric("Probability fake", f"{r['p_fake']:.0%}")

        st.subheader("Scam tactics found")
        if r["labels"]:
            for label in r["labels"].values():
                st.write(f"- {label}")
        else:
            st.write("None detected.")

        st.subheader("Highlighted phrases")
        st.markdown(
            f'<div style="white-space: pre-wrap;">{highlight(text, r["spans"])}</div>',
            unsafe_allow_html=True,
        )
        st.caption("Highlights show rule matches. Tactics found only by the classifier "
                   "have no highlighted phrase.")