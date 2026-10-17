# Recursive Travel AI ✈️

A Streamlit-based multi-agent travel itinerary prototype that uses iterative planning, critique, and revision to produce budget-conscious travel suggestions.

## What it does

Enter a destination, trip length, budget (USD), and preferences. The system drafts an itinerary, researches potential issues, verifies the draft, and revises it through a bounded improvement loop. The app displays the itinerary, final verification status, agent execution history, and a Markdown download option.

**Important:** Generated routes, opening hours, fares, and prices are estimates and may be incorrect. The app does not currently guarantee live map, transit, or venue data. A `FAIL` verification status means unresolved issues remain; do not treat the itinerary as verified.
## Agent workflow

```text
Trip details
    |
    v
Planner -> Researcher -> Verifier
                         |
               PASS -----+----> Final verification / budget checks
                         |
                        FAIL
                         |
                         v
                      Improver
                         |
                         +----> Researcher -> Verifier (bounded loop)

Final itinerary + verification status + execution history -> Streamlit UI
```

The orchestration layer coordinates agents and limits revision cycles rather than repeatedly generating unrestricted outputs. Verification failures are surfaced to the user rather than hidden.

## Tech stack

- Python
- Streamlit for the user interface
- HTTPX for API requests
- python-dotenv for local environment configuration
- Crusoe Cloud inference API using an open-weight Qwen model (check `llm_client.py` for the currently configured model identifier)

The repository is public, and model inference is configured to use an open-weight model. Hosted inference is not the same as running the model locally.

## Getting started

### 1. Clone

```bash
git clone https://github.com/Bkeskin10/recursive-travel-agents.git
cd recursive-travel-agents
```

### 2. Create and activate a virtual environment

Windows Git Bash:

```bash
python -m venv .venv
source .venv/Scripts/activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure the API key

Create a local `.env` file with:

```dotenv
CRUSOE_API_KEY=your_new_api_key_here
```

Never commit `.env` or real credentials. `.env.example` should contain a placeholder only. If a key is exposed in Git history, revoke it and create a new one; deleting it in a later commit is not enough.

### 5. Run the app

```bash
python -m streamlit run app.py
```

Open the local URL shown in the terminal (usually `http://localhost:8501`).

For command-line execution:

```bash
python main.py
```

## Repository structure

```text
recursive-travel-agents/
├── agents/
│   ├── planner.py
│   ├── researcher.py
│   ├── verifier.py
│   ├── improver.py
│   └── budget_validator.py
├── memory/
├── tests/
├── app.py
├── main.py
├── orchestrator.py
├── llm_client.py
├── requirements.txt
├── .env.example
└── README.md
```

## Testing

Run basic syntax and dependency checks:

```bash
python -m compileall -q app.py main.py orchestrator.py llm_client.py agents
python -m pip check
```

Test the end-to-end workflow from the Streamlit interface using a short trip and a modest budget. Check that the UI shows the itinerary, verification outcome, and execution history. A successful API call does not imply that every factual recommendation is correct.

## Known limitations

- The verifier can still flag unresolved routing, timing, or budget issues after the maximum number of improvement cycles.
- Model-generated budget tables can contain missing items or arithmetic inconsistencies; programmatic validation is limited by the information supplied to it.
- Place information, transit directions, prices, and opening hours are not guaranteed to be current.
- Output quality varies by model response and destination.

## Future improvements

- Structured itinerary and budget schemas with deterministic validation
- Verified routing, venue, and transit data integrations
- More comprehensive automated tests and evaluation cases
- Better execution-history visualization and error handling

## Hackathon demo

1. Enter a destination, number of days, budget, and interests.
2. Click **Generate itinerary**.
3. Review the itinerary and budget estimate.
4. Expand the final verification report to see unresolved issues.
5. Inspect the agent execution history to see the recursive review cycles.
6. Download the itinerary as Markdown.

## License

No license is declared in this README. Add an appropriate open-source license file if you intend to grant reuse permissions.
