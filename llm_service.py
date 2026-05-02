import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


# Load environment variables
load_dotenv()


# Initialize LLM
llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0.7
)


# def generate_guest_response(prompt):

#     response = llm.invoke(prompt)

#     return response.content

def generate_guest_response(prompt):

    print("\n MOCK LLM RESPONSE GENERATED")

    return "Certainly! Your request has been received and our hotel staff will assist you shortly."