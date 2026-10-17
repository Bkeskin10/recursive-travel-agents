"""Coordinate itinerary creation, bounded improvement, and final checks."""

from agents.planner import create_plan
from agents.researcher import research_itinerary
from agents.verifier import verify_itinerary
from agents.improver import improve_itinerary
from agents.budget_validator import validate_budget

MAX_IMPROVEMENT_CYCLES = 3


def get_verification_status(verification):
    """Fail closed if the verifier omits a recognizable status line."""
    if not isinstance(verification, str):
        return "FAIL"
    for line in verification.splitlines():
        line = line.strip().replace("**", "").upper()
        if line.startswith("STATUS:"):
            value = line.split(":", 1)[1].strip()
            return "PASS" if value == "PASS" else "FAIL"
    return "FAIL"


def run_agents(destination, days, budget, preferences, expenses=None, stated_total=None):
    print("\n[1] Planner generating itinerary...")
    itinerary = create_plan(destination, days, budget, preferences)
    if not isinstance(itinerary, str) or not itinerary.strip():
        raise RuntimeError("Planner returned an empty itinerary")

    history = []
    prior_feedback = []
    seen_itineraries = {itinerary.strip()}
    improvement_count = 0
    stop_reason = ""

    # Verify every candidate, including the final revision. A successful
    # verification is reused rather than calling the verifier again.
    for check_number in range(1, MAX_IMPROVEMENT_CYCLES + 2):
        print(f"\n=== Verification {check_number} ===")
        research = research_itinerary(itinerary, destination, budget)
        verification = verify_itinerary(itinerary, research, budget)
        llm_status = get_verification_status(verification)
        history.append({
            "iteration": check_number,
            "status": llm_status,
            "verification": verification,
            "improved_after": False,
        })
        print(f"Verifier: {llm_status}")

        if llm_status == "PASS":
            stop_reason = "Verifier passed the current itinerary"
            break
        if improvement_count >= MAX_IMPROVEMENT_CYCLES:
            stop_reason = "Maximum improvement cycles reached"
            break

        # Prior feedback is guidance, not proof that an issue remains present.
        revised = improve_itinerary(
            itinerary, research, verification,
            previous_feedback=prior_feedback[-2:],
            destination=destination, days=days, budget=budget,
            preferences=preferences,
        )
        if not isinstance(revised, str) or not revised.strip():
            stop_reason = "Improver returned an empty itinerary"
            break
        revised = revised.strip()
        if revised in seen_itineraries:
            stop_reason = "Improver repeated an earlier itinerary"
            break

        prior_feedback.append(verification[:2500])
        seen_itineraries.add(revised)
        history[-1]["improved_after"] = True
        itinerary = revised
        improvement_count += 1
    else:
        stop_reason = "Verification loop ended"

    print("\n[Final] Deterministic budget validation...")
    # This checks supplied structured expenses, NOT the prose budget in the
    # generated itinerary. Missing structured inputs must not be a PASS.
    budget_result = validate_budget(
        budget_limit=budget,
        expenses=expenses,
        stated_total=stated_total,
    )
    budget_status = budget_result.get("status", "NOT_CHECKED")
    if llm_status == "FAIL" or budget_status == "FAIL":
        final_status = "FAIL"
    elif llm_status == "PASS" and budget_status == "PASS":
        final_status = "PASS"
    else:
        final_status = "NOT_FULLY_VERIFIED"

    return {
        "itinerary": itinerary,
        "verification": verification,
        "status": final_status,
        "llm_status": llm_status,
        "budget_validation": budget_result,
        "execution_history": history,
        "improvement_cycles": improvement_count,
        "stop_reason": stop_reason,
    }
