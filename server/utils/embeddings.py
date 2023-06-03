import os
from langchain.embeddings import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

def get_embeddings(summary):
    """
    Given a summary, return the embeddings
    """
    embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
    embed = embeddings.embed_query(summary)
    return embed

if __name__ == "__main__":
    # testing
    summary = "I want to create a new project called 'test' with the description 'test'"
    print(get_embeddings(summary))
    # Print type
    print(type(get_embeddings(summary)[0]))