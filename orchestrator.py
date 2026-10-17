
from agents.planner import create_plan
from agents.researcher import research_itinerary
from agents.verifier import verify_itinerary
from agents.improver import improve_itinerary
from agents.budget_validator import validate_budget
import re


MAX_IMPROVEMENT_CYCLES = 3


def get_verification_status(verification):
    """
    Return PASS only when the verifier explicitly passes
    and does not report unresolved issues.
    """
    if not isinstance(verification, str) or not verification.strip():
        return "FAIL"

    status_match = re.search(
        r"^\s*STATUS:\s*(PASS|FAIL)\s*$",
        verification,
        flags=re.IGNORECASE | re.MULTILINE,
    )

    if not status_match:
        return "FAIL"

    if status_match.group(1).upper() != "PASS":
        return "FAIL"

    issues_match = re.search(
        r"^\s*ISSUES:\s*(.*?)(?=^\s*(?:RECOMMENDATIONS|STATUS):|\Z)",
        verification,
        flags=re.IGNORECASE | re.MULTILINE | re.DOTALL,
    )

    if not issues_match:
        # Require an explicit issues section.
        return "FAIL"

    issues = issues_match.group(1).strip()

    if not issues:
        return "PASS"

    if re.fullmatch(
        r"(?:none|no issues|no issues found|n/a|not applicable|0|"
        r"no critical issues|no unresolved issues)[.!]?",
        issues,
        flags=re.IGNORECASE,
    ):
        return "PASS"

    # Nonempty unresolved issue descriptions override PASS.
    return "FAIL"



def run_agents(
    destination,
    days,
    budget,
    preferences,
    expenses=None,
    stated_total=None,
):
    print("\n[1] Planner generating itinerary...")

    itinerary = create_plan(
        destination, days, budget, preferences
    )

    if not isinstance(itinerary, str) or not itinerary.strip():
        raise RuntimeError("Planner returned an empty itinerary")

    # Track the recursive agent workflow.
    execution_history = []
    improvement_cycles = 0
    stop_reason = ""
    seen_itineraries = {itinerary.strip()}

    final_verification = ""
    llm_status = "FAIL"

    # Three improvement opportunities plus final verification.
    for iteration in range(1, MAX_IMPROVEMENT_CYCLES + 2):

        print(f"\n=== Verification cycle {iteration} ===")

        print("[2] Researcher reviewing...")
        research = research_itinerary(
            itinerary, destination, budget
        )

        print("[3] Verifier checking...")
        verification = verify_itinerary(
            itinerary, research, budget
        )

        llm_status = get_verification_status(verification)
        final_verification = verification

        print("\nVerification:")
        print(verification)

        execution_history.append({
            "iteration": iteration,
            "status": llm_status,
            "verification": verification,
            "improved_after": False,
        })

        if llm_status == "PASS":
            print("\nItinerary passed verification!")
            stop_reason = "Verifier passed the current itinerary"
            break

        if improvement_cycles >= MAX_IMPROVEMENT_CYCLES:
            stop_reason = "Maximum improvement cycles reached"
            break

        print("[4] Improver revising...")

        revised = improve_itinerary(
            itinerary, research, verification
        )

        if not isinstance(revised, str) or not revised.strip():
            print("Improver returned empty output.")
            stop_reason = "Improver returned an empty itinerary"
            break

        revised = revised.strip()

        if revised in seen_itineraries:
            print("Improver repeated an earlier itinerary.")
            stop_reason = "Improver repeated an earlier itinerary"
            break

        seen_itineraries.add(revised)
        execution_history[-1]["improved_after"] = True

        itinerary = revised
        improvement_cycles += 1

    # -------------------------------------------------
    # DETERMINISTIC BUDGET VALIDATION
    # -------------------------------------------------

    print("\n[5] Deterministic budget validation...")

    budget_estimated = expenses is None

    if budget_estimated:
        # Estimated allocation, NOT actual itinerary expenses.
        expenses = {
            "food": round(budget * 0.50, 2),
            "transport": round(budget * 0.20, 2),
            "activities": round(budget * 0.20, 2),
            "miscellaneous": round(budget * 0.10, 2),
        }

        # Do not compare a stated itinerary total to
        # an independently invented allocation.
        validation_stated_total = None
    else:
        validation_stated_total = stated_total

    budget_result = validate_budget(
        budget_limit=budget,
        expenses=expenses,
        stated_total=validation_stated_total,
    )

    # An estimated allocation must not count as
    # verified itinerary expenses.
    if budget_estimated and budget_result["status"] == "PASS":
        budget_result["status"] = "NOT_CHECKED"
        budget_result["message"] = (
            "Estimated budget allocation arithmetic is valid, "
            "but actual itinerary expenses have not been verified."
        )

    budget_result["estimated_allocation"] = budget_estimated

    print("Budget validation:", budget_result["status"])
    print(budget_result["message"])

    # -------------------------------------------------
    # FINAL STATUS
    # -------------------------------------------------

    budget_status = budget_result["status"]

    if llm_status == "FAIL" or budget_status == "FAIL":
        final_status = "FAIL"

    elif llm_status == "PASS" and budget_status == "PASS":
        final_status = "PASS"

    else:
        final_status = "NOT_FULLY_VERIFIED"

    if final_status != "PASS":
        print("\nWARNING: Final itinerary is not fully verified.")

    print("\n=== FINAL TRAVEL ITINERARY ===")
    print(itinerary)

    print("\n=== EXECUTION SUMMARY ===")
    print("Improvement cycles:", improvement_cycles)
    print("Verification records:", len(execution_history))
    print("Stop reason:", stop_reason)
    print("Final status:", final_status)

    return {
        "itinerary": itinerary,
        "verification": final_verification,
        "status": final_status,
        "llm_status": llm_status,
        "budget_validation": budget_result,
        "execution_history": execution_history,
        "improvement_cycles": improvement_cycles,
        "stop_reason": stop_reason,
    }
