import os, hashlib, json
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
from pypdf import PdfReader
from job_search_agent.schema import Profile

CACHE_DIR = Path(__file__).resolve().parent.parent.parent / ".cache" / "profiles"

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
        {"role": "system", "content": "You are a skilled assistant who's job is to\
          extract structured information from a professional CV give as input to\
          you in form of a string."},   # tell it its job, one sentence
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
    profile = Profile.model_validate_json(json_str)

    # 8. Return it
    return profile

def get_or_extract_profile() -> Profile:
    """Return the cached Profile if this exact CV was extracted before,
    otherwise extract it fresh via Groq and cache the result."""
    pdf_path = os.getenv("TEST_CV_PATH")

    with open(pdf_path, "rb") as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()[:16]

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = CACHE_DIR / f"{file_hash}.json"

    if cache_path.exists():
        print(f"CV unchanged — using cached profile ({cache_path.name})")
        return Profile.model_validate_json(cache_path.read_text())

    print("CV changed (or first run) — extracting profile via Groq...")
    text = extract_pdf()
    profile = extract_profile(text)
    cache_path.write_text(profile.model_dump_json(indent=2))
    return profile

def main() -> None:
    smoke_test()
    text = extract_pdf()
    profile = extract_profile(text)
    # print(profile.model_dump_json(indent=2))


if __name__ == "__main__":
    main()