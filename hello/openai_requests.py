import openai
from dotenv import load_dotenv
import os

load_dotenv('.env')

openai.api_key = os.environ.get("OPENAI_API_KEY")

def get_embedding(text, model="text-embedding-ada-002"):
   text = text.replace("\n", " ")
   response = openai.Embedding.create(input = [text], model=model)
#    print(response)
   return response['data'][0]['embedding']