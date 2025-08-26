import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from llama_index.core.tools import FunctionTool
from dotenv import load_dotenv
import json
load_dotenv()

# Set up Google Sheets API credentials
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
try:
    # Local (with .env) or Production (e.g., Azure): Load from environment variable
    json_str = os.environ.get("GOOGLE_CREDENTIALS_JSON")
    if not json_str:
        raise Exception("No Google credentials found in file or environment variable")
    json_data = json.loads(json_str)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(json_data, scope)

    client = gspread.authorize(creds)
except Exception as e:
    raise Exception(f"Failed to initialize Google Sheets client: {str(e)}")

def retrieve_data(worksheet_name: str) -> str:
    """
    Retrieve data from a specified worksheet in the Google Sheet 'test_read_selah_gsheet'.
    Args:
        worksheet_name (str): Name of the worksheet to retrieve data from.
    Returns:
        str: JSON representation of the worksheet data.
    """
    try:
        sheet = client.open("test_read_selah_gsheet").worksheet(worksheet_name)
        data = sheet.get_all_values()
        df = pd.DataFrame(data[1:], columns=data[0])
        return df.to_json(orient="records")  # Return JSON string for LLM compatibility
    except Exception as e:
        return f"Error retrieving data: {str(e)}"

# Create LlamaIndex FunctionTool
retrieve_data_tool = FunctionTool.from_defaults(
    fn=retrieve_data,
    name="retrieve_data",
    description="Retrieve data from a specified worksheet in the Google Sheet 'test_read_selah_gsheet'. Provide the worksheet name as input."
)