import os
from google import genai
from dotenv import load_dotenv


def main() -> None:
    """
    Simple helper script to verify that the configured Gemini API key works.
    Reads the key from the GEMINI_API_KEY environment variable (via .env).
    """
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("Error: GEMINI_API_KEY is not set. Please add it to your .env file.")
        return

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Hello from TrustLens API key check!",
        )
        print("API Key is Working: " + response.text.strip())
    except Exception as e:
        print("Error while calling Gemini API: " + str(e))


if __name__ == "__main__":
    main()
