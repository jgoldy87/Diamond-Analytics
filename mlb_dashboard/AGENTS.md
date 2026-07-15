# Diamond Analytics

Diamond Analytics is an MLB analytics dashboard built with Python, Streamlit, Pandas, Plotly, and the MLB Stats API.

## Architecture

- `mlb_dashboard/api/` contains API functions.
- `mlb_dashboard/pages/` contains Streamlit pages.
- `app.py` controls navigation and routing.

## Development guidelines

- Preserve the existing UI style.
- Reuse helper functions when possible.
- Do not remove existing functionality without approval.
- Test Streamlit pages after changes.

## Roadmap

1. Finish Player Explorer:
   - Career statistics
   - Advanced splits
   - Rolling metrics

2. Team Comparison

3. Historical analytics using Lahman data

4. Advanced sabermetrics

5. UI polish