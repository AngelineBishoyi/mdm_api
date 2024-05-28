from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as gen_ai
import os
import logging
import uvicorn
from typing import List
# Load environment variables
load_dotenv()


app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)

class RecordsRequest(BaseModel):
    records: List[str]

@app.post("/generate-tables/")
async def generate_tables(request: RecordsRequest):
    print("hrdthy")
    user_prompt = request
    print(user_prompt)
    
    # Configure Google Generative AI
    GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
    print(GOOGLE_API_KEY)
    gen_ai.configure(api_key=GOOGLE_API_KEY)
    model = gen_ai.GenerativeModel("gemini-pro")
    
    # Define the prompt
    prompt = "hello"
    try:
        # Send user input to Gemini Pro with the prompt
        gemini_response = model.generate_content(prompt)
        print("Generating Response hold on")
        response_text = gemini_response.text
        print(response_text)
        logging.info(f"Gemini Pro response: {response_text}")
    except Exception as e:
        # Log the error
        logging.error(f"Error generating response: {e}")

        # Raise HTTPException with a meaningful error message
        raise HTTPException(status_code=500, detail="Internal Server Error")

    # Return the response
    return {"response": response_text}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)