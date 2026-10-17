"""Improve a travel itinerary using current and previous verifier feedback."""

from llm_client import ask_llm


def improve_itinerary(
    itinerary, research, verification, previous_feedback=None,
    destination=None, days=None, budget=None, preferences=None,
):
    system_prompt = """You are a travel itinerary improvement agent.
Correct the current verifier's concrete issues while preserving valid content.
The verifier may itself be wrong: treat unsupported claims as uncertainties,
not verified facts. Do not invent routes, fares, opening hours, or evidence.
Do not assume dates, hotel locations, or missing user constraints.

Requirements:
- Include every requested day and preserve the traveler's preferences.
- Group nearby places, avoid backtracking, and allow transit buffers.
- Fix feasible, supported issues; disclose anything that cannot be verified.
- Do not reintroduce issues from prior rounds that remain applicable.
- Keep the itinerary under 1800 words and return complete Markdown.
- Show an itemized budget with nonnegative expenses, an explicit sum, and
  remaining budget. Separate optional expenses from included expenses.
- Do not assert that estimated prices or routes have been live-verified.
- Avoid adding activities just to fill unused budget.
- Do not include a separate revision log.
"""
    # Keep the feedback context bounded to avoid crowding out the itinerary.
    previous_feedback = previous_feedback or []
    historical_notes = "\n\n".join(str(item)[:1600] for item in previous_feedback[-2:])
    user_prompt = f"""TRAVEL REQUIREMENTS:
Destination: {destination or 'Not supplied'}
Days: {days if days is not None else 'Not supplied'}
Budget limit: {budget if budget is not None else 'Not supplied'}
Preferences: {preferences if preferences is not None else 'Not supplied'}

CURRENT ITINERARY:
{itinerary}

CURRENT RESEARCH:
{research}

LATEST VERIFICATION (address these issues first):
{verification}

PRIOR VERIFICATION FEEDBACK (avoid regressions, but reassess applicability):
{historical_notes or 'None'}

Return the complete revised itinerary, including all days and budget.
If a claim cannot be verified, mark it as an estimate or uncertainty.
"""
    return ask_llm(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        max_tokens=2500,
    )
