import sys
sys.stdout.reconfigure(encoding="utf-8")
from orchestrator import run_agents


def main():
    print("=== Recursive Travel Agents ===")

    destination = "San Francisco"
    days = 2
    budget = 300
    preferences = "Nature, sightseeing, affordable food"

    print("\nStarting multi-agent travel planning...\n")

    itinerary = run_agents(
        destination=destination,
        days=days,
        budget=budget,
        preferences=preferences
    )

    print("\n=== FINAL TRAVEL ITINERARY ===\n")
    print(itinerary)


if __name__ == "__main__":
    main()
