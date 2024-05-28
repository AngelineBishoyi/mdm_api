from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as gen_ai
import os
import logging
from typing import List, Dict

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize FastAPI app
app = FastAPI()

# Define Pydantic model for request body
class RecordsRequest(BaseModel):
    records: List[str]

# Function to parse the input string into a list of dictionaries
def parse_records(record_string: str) -> List[Dict[str, str]]:
    records = []
    for record in record_string.split(" first_name : "):
        if record.strip():
            fields = record.strip().split(", ")
            record_dict = {}
            for field in fields:
                key, value = field.split(": ")
                record_dict[key.strip()] = value.strip()
            records.append(record_dict)
    return records

@app.post("/generate-tables/")
async def generate_tables(request: RecordsRequest):
    # Log the incoming request
    logging.info("Received request with records")
    
    # Configure Google Generative AI
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    if not GOOGLE_API_KEY:
        logging.error("Google API key not configured")
        raise HTTPException(status_code=500, detail="Google API key not configured")
    
    try:
        gen_ai.configure(api_key=GOOGLE_API_KEY)
        model = gen_ai.GenerativeModel("gemini-pro")
    except Exception as e:
        logging.error(f"Error configuring Google Generative AI: {e}")
        raise HTTPException(status_code=500, detail="Error configuring Google Generative AI")
    
    unique_records = []
    duplicate_records = []
    similar_records = []
    
    try:
        # Process each record string in the request
        for record_string in request.records:
            parsed_records = parse_records(record_string)
            for record in parsed_records:
                # Define the prompt for the model
                prompt = f"Classify the following record: {record}"
                try:
                    gemini_response = model.generate_content(prompt)
                    response_text = gemini_response.text.strip().lower()
                    
                    # Log the response from the model
                    logging.info(f"Response for record {record}: {response_text}")
                    
                    # Classify the record based on the response
                    if response_text == "unique":
                        unique_records.append(record)
                    elif response_text == "duplicate":
                        duplicate_records.append(record)
                    elif response_text == "similar":
                        similar_records.append(record)
                    else:
                        logging.warning(f"Unexpected response for record {record}: {response_text}")
                except Exception as e:
                    logging.error(f"Error generating content for record {record}: {e}")
                    raise HTTPException(status_code=500, detail="Error generating content")

    except Exception as e:
        # Log the error
        logging.error(f"Error processing records: {e}")
        raise HTTPException(status_code=500, detail="Error processing records")

    # Return the categorized records
    return {
        "unique_records": unique_records,
        "duplicate_records": duplicate_records,
        "similar_records": similar_records
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
