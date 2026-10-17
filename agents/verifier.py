
from llm_client import ask_llm


def verify_itinerary(itinerary, research, budget):
    system_prompt = """
You are a travel itinerary verification agent.

Evaluate whether the itinerary:
1. Respects the stated budget
2. Has a logical daily schedule
3. Addresses the researcher's concerns
4. Avoids unsupported factual claims
5. Is practical for a traveler

Do not invent facts.

Return exactly this structure:

STATUS: PASS or FAIL
ISSUES:
- List specific issues, or None
RECOMMENDATIONS:
- List suggested fixes, or None

Verify these specific areas:

1. Geography:
   - Check whether consecutive stops are reasonably close.
   - Flag unrealistic travel times or unnecessary backtracking.

2. Transportation:
   - Distinguish confirmed transit facts from estimates.
   - Flag unsupported route, fare, or pass claims.
   - Allow reasonable waiting and transfer buffers.

3. Budget:
   - Check that all listed expenses are nonnegative.
   - Check arithmetic in the itemized budget.
   - Check that remaining budget equals budget minus total.
   - Distinguish optional expenses from included expenses.

4. Schedule:
   - Ensure every requested travel day is included.
   - Flag overlapping activities or unrealistic transitions.
   - Do not assume a sunset time without a travel date.

5. Evidence:
   - Do not treat another agent's unsupported claim
     as independently verified.
   - Do not invent facts to justify a failure.
   - Explain uncertainty when evidence is insufficient.

For each critical issue, provide a specific actionable fix.
Do not fail an itinerary solely for minor stylistic preferences.

Only return PASS if there are no major issues.
"""

    user_prompt = f"""
Budget: ${budget}

Itinerary:
{itinerary}

Researcher findings:
{research}

Verify this itinerary.
"""

    return ask_llm(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        max_tokens=1000
    )
