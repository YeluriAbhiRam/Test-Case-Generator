# Test-Case-Generator
 
Step 1: Create & Activate Virtual Environment
Mac/Linux (Terminal)

python3 -m venv venv
source venv/bin/activate

Windows (Command Prompt)

python -m venv venv
venv\Scripts\activate

Step 2: Install Dependencies

pip install --upgrade pip
pip install -r requirements.txt

If you face dependency issues, try:

pip install --no-cache-dir -r requirements.txt

Step 3: Set Up Hugging Face Model (If Required)
If the application uses Hugging Face models, log in to the Hugging Face CLI:

huggingface-cli login
Alternatively, set the API key as an environment variable:

export HUGGINGFACEHUB_API_TOKEN=<your_api_key>

Step 4:Run the Application FastAPI:

uvicorn main:app --host 0.0.0.0 --port 8000 --reload

Step 5: Test the application:

Using POSTMAN with link http://127.0.0.1:8000/generate-test-cases POST call and 
body as raw JSON format:
{
  "requirements": [
   "Query1",
   "Query2
  ]
}

Step 6: Output:

Check the CSV file for output or the POSTMAN
