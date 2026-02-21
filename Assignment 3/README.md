# Assignment 3 - Streamlit GUI

## File locations
- Streamlit GUI file: `/Users/stephenchung/Desktop/Gradschool/2025-2026/Winter/ADSP 31026 Python for ML Engineering/Assignments/Assignment 3/score_headlines_gui.py`
- Assignment 2 API file: `/Users/stephenchung/Desktop/Gradschool/2025-2026/Winter/ADSP 31026 Python for ML Engineering/Assignments/Assignment 2/score_headlines_api.py`

## How to run
1. Start the API server first (Assignment 2):
   - `python "Assignment 2/score_headlines_api.py"`
2. Start Streamlit on a port that starts with `9` (example: `9001`):
   - `streamlit run "Assignment 3/score_headlines_gui.py" --server.port 9001`
3. Open the Streamlit URL in your browser and verify the API Base URL in the sidebar.

## Notes
- The GUI calls `POST /score_headlines` on the API server.
- The app lets users add/delete headline rows, bulk paste one headline per line, and then score all non-empty headlines.
