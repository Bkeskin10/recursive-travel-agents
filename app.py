import streamlit as st
from orchestrator import run_agents

st.set_page_config(page_title="Recursive Travel AI", page_icon="✈️", layout="wide")

st.title("✈️ Recursive Travel AI")
st.caption("Multi-agent travel planning with iterative review and verification")

with st.sidebar:
    st.header("Plan your trip")
    destination = st.text_input("Destination", value="San Francisco")
    days = st.number_input("Travel days", min_value=1, max_value=14, value=2, step=1)
    budget = st.number_input("Total budget (USD)", min_value=1, value=300, step=25)
    preferences = st.text_area("Preferences", value="Nature, sightseeing, affordable food", height=100)
    st.caption("Specify whether your budget includes accommodation and transportation in your preferences.")
    generate = st.button("✨ Generate itinerary", type="primary", use_container_width=True)

if "travel_result" not in st.session_state:
    st.session_state.travel_result = None

if generate:
    if not destination.strip():
        st.error("Please enter a destination.")
    else:
        st.session_state.travel_result = None
        with st.spinner("Agents are planning, researching, verifying, and improving your itinerary. This can take a few minutes..."):
            try:
                result = run_agents(destination.strip(), int(days), int(budget), preferences.strip())
                if isinstance(result, str):
                    result = {"itinerary": result, "verification": "Not returned by orchestrator", "status": "UNKNOWN"}
                if not isinstance(result, dict):
                    raise TypeError("Expected run_agents() to return a dictionary.")
                st.session_state.travel_result = result
            except Exception as exc:
                st.error(f"Travel planning failed: {exc}")
                st.info("Check the terminal for additional error details and verify your API key is configured.")

result = st.session_state.travel_result
if result:
    itinerary = str(result.get("itinerary") or "")
    verification = str(result.get("verification") or "No verification report returned.")
    status = str(result.get("status") or "UNKNOWN").strip().upper()

    st.subheader("Your travel itinerary")
    if status == "PASS":
        st.success("Final verification: PASS")
    elif status == "FAIL":
        st.warning("Final verification: FAIL — the itinerary may contain unresolved issues. Review before using it.")
    elif status == "NOT_FULLY_VERIFIED":
        st.warning("Final verification: NOT FULLY VERIFIED — some checks could not be completed.")
    else:
        st.info(f"Final verification status: {status}")

    if itinerary:
        st.markdown(itinerary)
        st.download_button(
            "⬇️ Download itinerary (.md)",
            data=itinerary,
            file_name="travel_itinerary.md",
            mime="text/markdown",
        )
    else:
        st.error("The agents returned an empty itinerary.")

    with st.expander("View final verification report", expanded=(status != "PASS")):
        st.text(verification)

    st.subheader("Agent Execution History")
    history = result.get("execution_history") or []
    cycles = result.get("improvement_cycles", 0)
    stop_reason = result.get("stop_reason") or "Not provided"

    metric1, metric2 = st.columns(2)
    metric1.metric("Improvement cycles", cycles)
    metric2.metric("Verification records", len(history) if isinstance(history, list) else 0)
    st.caption(f"Stop reason: {stop_reason}")

    if isinstance(history, list) and history:
        for index, entry in enumerate(history, start=1):
            with st.expander(f"Verification cycle {index}"):
                if isinstance(entry, (dict, list)):
                    st.json(entry)
                else:
                    st.write(str(entry))
    else:
        st.info("No execution history was returned by the orchestrator.")

    budget_result = result.get("budget_validation")
    if isinstance(budget_result, dict):
        with st.expander("Budget validation details"):
            st.json(budget_result)
else:
    st.info("Enter your travel details in the sidebar, then select Generate itinerary.")