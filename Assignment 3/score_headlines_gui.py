"""Streamlit UI for scoring headlines with the Assignment 2 API."""

from __future__ import annotations

import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import streamlit as st

API_URL = os.getenv("HEADLINE_API_URL", "http://127.0.0.1:8081")
TIMEOUT_SECONDS = 20

st.set_page_config(page_title="Headline Scoring", layout="wide")


def call_score_api(headlines: list[str]) -> list[str | int]:
    """Send headlines to the Assignment 2 API and return predicted labels."""
    endpoint = f"{API_URL.rstrip('/')}/score_headlines"
    req = Request(
        endpoint,
        data=json.dumps({"headlines": headlines}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(req, timeout=TIMEOUT_SECONDS) as res:
            response_labels = json.loads(res.read().decode("utf-8")).get("labels")
    except HTTPError as exc:
        raise RuntimeError(
            f"API returned HTTP {exc.code}: {exc.read().decode('utf-8', errors='replace')}"
        ) from exc
    except URLError as exc:
        raise RuntimeError(f"Unable to reach API at {endpoint}: {exc.reason}") from exc
    if not isinstance(response_labels, list):
        raise RuntimeError("API response missing 'labels' list")
    return response_labels


if "headlines" not in st.session_state:
    st.session_state.headlines = [""]
if "ui_version" not in st.session_state:
    st.session_state.ui_version = 0

st.title("Headline Sentiment Scoring")
st.caption("Edit headlines, add lines, then score them.")

if st.button("Add Headline"):
    st.session_state.headlines.append("")
    st.session_state.ui_version += 1
    st.rerun()

with st.expander("Bulk Paste Headlines"):
    bulk_text = st.text_area("Paste one headline per line")
    if st.button("Load Pasted Lines"):
        lines = [line.strip() for line in bulk_text.splitlines() if line.strip()]
        if lines:
            st.session_state.headlines = lines
            st.session_state.ui_version += 1
            st.rerun()
        else:
            st.warning("No non-empty lines found.")

row_to_delete: int | None = None
for i, headline in enumerate(st.session_state.headlines):
    left, right = st.columns([10, 1])
    key = f"headline_{st.session_state.ui_version}_{i}"
    if key not in st.session_state:
        st.session_state[key] = headline
    st.session_state.headlines[i] = left.text_input(f"Headline {i + 1}", key=key)
    if right.button("Delete", key=f"delete_{i}"):
        row_to_delete = i

if row_to_delete is not None:
    st.session_state.headlines.pop(row_to_delete)
    if not st.session_state.headlines:
        st.session_state.headlines = [""]
    st.session_state.ui_version += 1
    st.rerun()

if st.button("Score Headlines", type="primary"):
    cleaned = [h.strip() for h in st.session_state.headlines if h.strip()]
    if not cleaned:
        st.error("Add at least one headline before scoring.")
    else:
        with st.spinner("Calling scoring API..."):
            try:
                labels = call_score_api(cleaned)
            except RuntimeError as exc:
                st.error(str(exc))
            else:
                st.dataframe(
                    [
                        {
                            "headline": h,
                            "label": labels[i] if i < len(labels) else "n/a",
                        }
                        for i, h in enumerate(cleaned)
                    ],
                    use_container_width=True,
                )
