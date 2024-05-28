from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as gen_ai
import os
import logging
from typing import List

# Load environment variables
load_dotenv()

# Configure Google Generative AI
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
gen_ai.configure(api_key=GOOGLE_API_KEY)
model = gen_ai.GenerativeModel("gemini-pro")

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)

class RecordsRequest(BaseModel):
    records: List[str]

@app.post("/generate-tables/")
async def generate_tables(request: RecordsRequest):
    user_records = request.records
    
    # Define the prompt
    prompt = f"""
    From the provided records, I want you to generate three tables:

    1. Unique Records:
       Generate a table showing unique records based on the larger length of the first name. If there are multiple records with similar first names,
       select the one with the longest first name. Include the count of occurrences for each unique record. Only include records entered by the user
       in this table.

    2. Duplicate Records:
       Generate a table showing duplicate records based on the smaller length of the first name compared to unique records.
       If a duplicate record has the same first name as a unique record, increase the count of the unique record instead of listing it separately.
       Please only consider records from the user provided data, not any examples.

    3. Similar Records:
       Generate a table combining records with similar first names to those in the unique records table. Records with similar first names are those where 
       the first name matches the unique record's first name partially or entirely. Include the count of occurrences for each similar record.
       It should have only one record which is the combination of other similar records. There should be only one record in this table.

    Additionally, at the end provide a justification for the unique, duplicate, and similar records in one paragraph. For unique records, explain 
    why certain records were chosen as unique. For duplicate records, explain why they were identified as duplicates. For similar records, explain 
    the rationale behind combining them. Justifications should be concise, with a maximum of 300 words for unique records and 200 words for duplicates 
    and similar records.

    Justification should be displayed after displaying all three tables in a paragraph; I don't need separate justifications.
    """
    
    try:
        # Send user input to Gemini Pro with the prompt
        gemini_response = model.generate(prompt=user_records + prompt)
        response_text = gemini_response.text
        logging.info(f"Gemini Pro response: {response_text}")
    except Exception as e:
        # Log the error
        logging.error(f"Error generating response: {e}")

        # Raise HTTPException with a meaningful error message
        raise HTTPException(status_code=500, detail="Internal Server Error")

    # Return the response
    return {"response": response_text}
