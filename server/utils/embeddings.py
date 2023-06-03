import os
import numpy as np
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

def str_to_np_embed(embedding_str):
    try:
        embedding_str = embedding_str.replace("[", "").replace("]", "").replace("\n", "").replace(" ", "").split(",")
        embedding = np.array(embedding_str, dtype=np.float32)
        return embedding
    except Exception as e:
        print(e)
        return None