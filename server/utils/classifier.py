# import langchain
from langchain.llms import OpenAI
from langchain import PromptTemplate

import json
import os
from dotenv import load_dotenv

load_dotenv()


def get_conv_classification(convStr, projNames):
    """
    Given a conversation, get the project it belongs to
    """
    llm = OpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"), temperature=0, max_tokens=5)
    prompt = f"This conversation is about one of these projects {', '.join(projNames)}. Select which one. Return None if no project is related."
    # make llm call
    response = llm(prompt)
    return response

