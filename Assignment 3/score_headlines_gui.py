"""Streamlit UI for scoring news headlines with the assignment 2 API."""

from __future__ import annotations

import json
import os
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import streamlit as st

DEFAULT_API_URL = os.getenv("HEADLINE_API_URL", "http://127.0.0.1:8081")
DEFAULT_TIMEOUT_SECONDS = 20


st.set_page_config(page_title="Headline Scoring", page_icon="📰", layout="wide")


def call_score_api(
    api_base_url: str, headlines: list[str], request_timeout_seconds: int
) -> list[Any]:
    """Call the FastAPI service and return the list of labels."""
    endpoint = f"{api_base_url.rstrip('/')}/score_headlines"
    payload = {"headlines": headlines}
    body = json.dumps(payload).encode("utf-8")

    request = Request(
        endpoint,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(request, timeout=request_timeout_seconds) as response:
            response_body = response.read().decode("utf-8")
            parsed_response = json.loads(response_body)
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"API returned HTTP {exc.code}: {detail}") from exc
    except URLError as exc:
        raise RuntimeError(f"Unable to reach API at {endpoint}: {exc.reason}") from exc

    response_labels = parsed_response.get("labels")
    if not isinstance(response_labels, list):
        raise RuntimeError("API response missing 'labels' list")

    return response_labels


def initialize_state() -> None:
    """Create initial session state values."""
    if "headlines" not in st.session_state:
        st.session_state.headlines = [
            "Tech stocks rally as AI demand grows",
            "Oil prices fall after weak global demand report",
            "Retail sales beat expectations in January",
        ]


def cleaned_headlines_with_index(
    raw_headlines: list[str],
) -> tuple[list[int], list[str]]:
    """Return (indexes, cleaned_headlines) while preserving original order."""
    indexes: list[int] = []
    cleaned_headlines: list[str] = []

    for original_idx, value in enumerate(raw_headlines):
        trimmed_value = value.strip()
        if trimmed_value:
            indexes.append(original_idx)
            cleaned_headlines.append(trimmed_value)

    return indexes, cleaned_headlines


initialize_state()

st.title("Headline Sentiment Scoring")
st.caption(
    "Edit headlines, remove lines, then score them against your Assignment 2 API."
)

with st.sidebar:
    st.header("API Settings")
    api_url = st.text_input("Base URL", value=DEFAULT_API_URL)
    timeout_seconds = st.number_input(
        "Timeout (seconds)", min_value=1, max_value=120, value=DEFAULT_TIMEOUT_SECONDS
    )
    st.markdown("Run Streamlit on a 9081 port")

st.subheader("Headlines")
control_col_1, control_col_2, control_col_3 = st.columns(3)

if control_col_1.button("Add Headline"):
    st.session_state.headlines.append("")

if control_col_2.button("Remove Empty"):
    st.session_state.headlines = [h for h in st.session_state.headlines if h.strip()]

if control_col_3.button("Clear All"):
    st.session_state.headlines = [""]

with st.expander("Bulk Paste Headlines", expanded=False):
    bulk_text = st.text_area(
        "Paste one headline per line",
        placeholder=(
            "Example:\nFed signals rates may stay higher\n"
            "Company X beats earnings forecasts"
        ),
    )
    if st.button("Load Pasted Lines"):
        parsed_lines = [line.strip() for line in bulk_text.splitlines() if line.strip()]
        if parsed_lines:
            st.session_state.headlines = parsed_lines
            st.success(f"Loaded {len(parsed_lines)} headlines.")
        else:
            st.warning("No non-empty lines found.")

row_to_delete: int | None = None
for idx, current_headline in enumerate(st.session_state.headlines):
    editor_col, delete_col = st.columns([10, 1])
    key = f"headline_input_{idx}"
    new_value = editor_col.text_input(
        f"Headline {idx + 1}",
        value=current_headline,
        key=key,
        label_visibility="visible",
    )

    if new_value != current_headline:
        st.session_state.headlines[idx] = new_value

    if delete_col.button("Delete", key=f"delete_{idx}"):
        row_to_delete = idx

if row_to_delete is not None:
    st.session_state.headlines.pop(row_to_delete)
    if not st.session_state.headlines:
        st.session_state.headlines = [""]
    st.rerun()

score_clicked = st.button("Score Headlines", type="primary")

if score_clicked:
    keep_indexes, cleaned = cleaned_headlines_with_index(st.session_state.headlines)

    if not cleaned:
        st.error("Add at least one non-empty headline before scoring.")
    else:
        with st.spinner("Calling scoring API..."):
            try:
                labels = call_score_api(api_url, cleaned, int(timeout_seconds))
            except RuntimeError as exc:
                st.error(str(exc))
            else:
                if len(labels) != len(cleaned):
                    st.error(
                        "API returned a different number of labels than "
                        "headlines. Check your server implementation."
                    )
                else:
                    label_by_index = dict(zip(keep_indexes, labels, strict=False))

                    result_rows = []
                    for i, headline in enumerate(st.session_state.headlines):
                        stripped = headline.strip()
                        result_rows.append(
                            {
                                "headline": stripped if stripped else "(empty)",
                                "label": label_by_index.get(i, "n/a"),
                            }
                        )

                    st.success("Scoring complete.")
                    st.dataframe(result_rows, use_container_width=True)
