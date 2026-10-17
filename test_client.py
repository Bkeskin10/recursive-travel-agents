
from llm_client import ask_llm

def main():
    print("Testing Crusoe API connection...")

    response = ask_llm(
        system_prompt="You are a helpful travel assistant.",
        user_prompt="Suggest three activities in San Francisco.",
        max_tokens=300
    )

    print("\nModel response:")
    print(response)

if __name__ == "__main__":
    main()

