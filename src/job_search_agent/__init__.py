import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# This is a smoke test to verify that the Groq API is working correctly. 
# It sends a simple request to the API and checks if a valid response is received.
def smoke_test():
    api_key = os.getenv("GROQ_API_KEY")
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that translates English to French."
            },
            {
                "role": "user",
                "content": "Translate the following English text to French: 'Hello, how are you?'"
            }
        ]
    )
    if(response and response.choices and len(response.choices) > 0):
        print("Smoke test passed! Translation:", response.choices[0].message.content)


def main() -> None:
    smoke_test()
    print("Hello from job-search-agent!")

if __name__ == "__main__":
    main()
