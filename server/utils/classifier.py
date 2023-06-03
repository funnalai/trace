# import langchain
from langchain.llms import OpenAI
from langchain import PromptTemplate

import json
import os
from dotenv import load_dotenv
from langchain import Document, load_summarize_chain
load_dotenv()


def get_conv_classification(convStr, projNames):
    """
    Given a conversation, get the project it belongs to
    """
    llm = OpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"), temperature=0.7, max_tokens=5)
    prompt = f"{convStr}\n This conversation is about one of these projects {', '.join(projNames)}. Select which project matches the conversation best. Return None if no project is related."
    # make llm call
    response = llm(prompt)
    return response

def get_natural_convs_title(summaries):
    """
    Create few-word, topic-based summarization of a list of conversation summaries
    """
    llm = OpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"), temperature=0)
    docs = [Document(page_content=text) for text in summaries]
    prompt = """
    Write a title for the following summaries of conversations
    "{text}"
    TITLE:
    """
    prompt_template = PromptTemplate(template=prompt, input_variables=["text"])

    summarize_chain = load_summarize_chain(
        llm, chain_type="stuff", prompt=prompt_template)
    title = summarize_chain.run(docs)
    return title
