import os
from dotenv import load_dotenv
from groq import Groq
from pypdf import PdfReader

from job_search_agent.schema import Profile

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
    reader = PdfReader(os.getenv("TEST_CV_PATH"))
    print(len(reader.pages))

    text = reader.pages[0].extract_text()
    return text

def extract_profile(text: str) -> Profile:
    # 1. Build the client
    api_key = os.getenv("GROQ_API_KEY")
    client = Groq(api_key=api_key)

    # 2. Turn Profile into a JSON Schema dict
    schema = Profile.model_json_schema()

    # 3. Wrap it in the shape Groq expects
    response_format = {
        "type": "json_schema",
        "json_schema": {
            "name": "profile",
            "strict": True,
            "schema": schema
        }
    }

    # 4. Build the messages list — same pattern as smoke_test, different content
    messages = [
        {"role": "system", "content": "You are a skilled assistant who's job is to extract structured information from a professional CV give as input to you in form of a string."},   # tell it its job, one sentence
        {"role": "user", "content": text} 
    ]

    # 5. Make the call
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=messages,
        response_format=response_format
    )

    # 6. Pull the JSON string out 
    json_str = response.choices[0].message.content

    # 7. Parse it into a real Profile object
    profile = Profile.parse_raw(json_str)

    # 8. Return it
    return profile

def main() -> None:
    smoke_test()
    text = extract_pdf()
    profile = extract_profile(text)
    print(profile.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
