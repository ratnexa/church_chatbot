from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from llama_index.core.agent.workflow import FunctionAgent
from tools import retrieve_data_tool
from llama_index.llms.openai import OpenAI
import os
from datetime import date
from dotenv import load_dotenv
from llama_index.core import PromptTemplate
import asyncio

# Load environment variables
load_dotenv()

# Define a detailed agent prompt
AGENT_PROMPT_TEXT = """
Eres un asistente trabajando para el grupo de la iglesia. Tu tarea será leer de una hoja de una google sheet para ayudar a ayudarnos a coordinar las funciones y recordatorios del grupo tales como:
- Fechas de cumpleaños y datos generales de asistentes (Hoja: "BASE DE DATOS GENERAL" y tambien en la hoja "NUEVOS")
- Funciones del grupo (Hoja: "FUNCIONES")
- Descripcion de personas nuevas (Hoja: "NUEVOS")
- Cronograma de actividades del grupo (Hoja: "CRONOGRAMA") (Acá se incluye información de quien tiene a cargo la expectativa para el grupo en la semana y la actividad de la semana)

Solamente podrás escoger de las hojas que se te han descrito acá. No debes crear ninguna otra ni llamar a ninguna otra.

Para esto, tendrás acceso a la funcion "retrieve_data" que utilizarás de acuerdo a lo que se te pregunte.
Adicionalmente, ten en cuenta los siguientes datos:
- Hoy es {todays_date}
"""


AGENT_PROMPT = PromptTemplate(AGENT_PROMPT_TEXT)

# Get today's date
today = date.today()
formatted_date = today.strftime("%Y-%m-%d")

# Initialize FastAPI app
app = FastAPI(title="LlamaIndex Agent API")

# Initialize OpenAI LLM
try:
    llm = OpenAI(
        model="gpt-4o",
        api_key=os.getenv("OPENAI_API_KEY")
    )
except Exception as e:
    raise Exception(f"Failed to initialize OpenAI LLM: {str(e)}")

# Create an agent with the tool
try:
    agent = FunctionAgent(
        tools=[retrieve_data_tool],
        llm=llm,
        system_prompt=AGENT_PROMPT.format(todays_date=formatted_date)
    )
except Exception as e:
    raise Exception(f"Failed to initialize agent: {str(e)}")

# Define input model
class ChatInput(BaseModel):
    message: str

@app.get("/")
async def root():
    return {"message": "LlamaIndex Agent API is running"}

@app.post("/chat")
async def chat(input_data: ChatInput):
    try:
        # Use run_async to handle async workflow
        response = await agent.run(input_data.message)
        return {"response": str(response)}
    except Exception as e:
        print(f"Error in /chat: {str(e)}")  # Log error for debugging
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")