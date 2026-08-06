import os
from dotenv import load_dotenv
from groq import Groq
from pypdf import PdfReader

load_dotenv()

# This is a smoke test to verify that the Groq API is working correctly. 
# It sends a simple request to the API and checks if a valid response is received.
def smoke_test():
    api_key = os.getenv("GROQ_API_KEY")
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
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

def extract_pdf():
    reader = PdfReader('TanuCV_Aug.pdf')
    print(len(reader.pages))

    text = reader.pages[0].extract_text()
    return text

def extract_profile():
    text = extract_pdf()

def main() -> None:
    smoke_test()
    extract_pdf()
    print("Hello from job-search-agent!")

if __name__ == "__main__":
    main()
