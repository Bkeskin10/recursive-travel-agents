
from llm_client import ask_llm

def create_plan(destination, days, budget, preferences):
    system_prompt = """
    You are an expert travel planning agent.
    Create practical, detailed travel itineraries.
    Organize activities by day.
    Respect the budget and user preferences.
    Do not invent prices or opening hours.
    """

    user_prompt = f"""
    Destination: {destination}
    Days: {days}
    Budget: ${budget}
    Preferences: {preferences}

    Create a detailed day-by-day itinerary.
    """

    return ask_llm(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        max_tokens=2500
    )
