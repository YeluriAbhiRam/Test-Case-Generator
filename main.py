import os
import csv
import logging
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi.responses import FileResponse
from transformers import pipeline
from huggingface_hub import login

# Load environment variables
load_dotenv()

# Log in to Hugging Face
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
login(token=HUGGINGFACE_API_KEY)

# Initialize FastAPI
app = FastAPI()

# Define the request model
class JiraEpicRequirements(BaseModel):
    requirements: list[str]

# Load a Hugging Face model for text generation
model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"  # You can replace this with any Hugging Face model
text_generator = pipeline("text-generation", model=model_name)

def generate_test_cases(requirement):
    # Use prompt engineering to guide the model
    prompt = f"""
    You are a QA engineer. Generate test cases in JSON format.

    The requirement: "{requirement}"

    Output in this exact JSON format:
    {{
    "test_cases": [
        {{
        "test_case_id": "TC001",
        "test_case_description": "Description here",
        "steps": ["Step 1", "Step 2", "Step 3"],
        "expected_result": "Expected result here"
        }}
    ]
    }}
    """

    try:
        # Generate text using the Hugging Face model
        response = text_generator(
            prompt,
            max_length=512,
            num_return_sequences=1,
            temperature=0.7,
            do_sample=True,  # Enable sampling-based generation
            truncation=True,  # Explicitly enable truncation
        )
        generated_text = response[0]["generated_text"].strip()

        # Extract JSON from the generated text
        json_start = generated_text.find("{")
        json_end = generated_text.rfind("}") + 1
        json_output = generated_text[json_start:json_end]

        return json_output
    except Exception as e:
        logging.error(f"Error generating test cases: {e}")
        raise

# Parse the generated test case output
def parse_test_case_output(output):
    try:
        # Parse the JSON output
        data = json.loads(output)
        test_cases = data.get("test_cases", [])

        # Convert to the desired format
        parsed_test_cases = []
        for test_case in test_cases:
            parsed_test_cases.append({
                "Test Case ID": test_case.get("test_case_id", "N/A"),
                "Test Case Description": test_case.get("test_case_description", "N/A"),
                "Steps": "\n".join(test_case.get("steps", [])),
                "Expected Result": test_case.get("expected_result", "N/A"),
            })

        return parsed_test_cases
    except json.JSONDecodeError as e:
        logging.error(f"Error parsing JSON output: {e}")
        return []

# Save test cases to a CSV file
def save_test_cases(test_cases, filename="test_cases.csv"):
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Test Case ID", "Test Case Description", "Steps", "Expected Result"])
        for test_case in test_cases:
            writer.writerow([
                test_case["Test Case ID"],
                test_case["Test Case Description"],
                test_case["Steps"],
                test_case["Expected Result"],
            ])

# API endpoint to generate test cases
@app.post("/generate-test-cases")
async def generate_test_cases_api(requirements: JiraEpicRequirements):
    try:
        # Generate test cases for each requirement
        all_test_cases = []
        for requirement in requirements.requirements:
            print(f"Generating test cases for requirement: {requirement}")
            test_case_output = generate_test_cases(requirement)
            print(test_case_output)

            # Parse the test case output
            test_cases = parse_test_case_output(test_case_output)
            all_test_cases.extend(test_cases)

        # Save test cases to a CSV file
        save_test_cases(all_test_cases)
        print("Test cases saved to test_cases.csv")

        # Return the CSV file as a response
        return FileResponse("test_cases.csv", media_type="text/csv", filename="test_cases.csv")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the FastAPI app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
