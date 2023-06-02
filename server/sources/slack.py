import datetime
import os
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from langchain.llms import OpenAI
from langchain import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document


load_dotenv()

def summarize_conversation(raw_conv):
    """
    Summarize a conversation based on its raw messages
    """
    # return ""
    llm = OpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"), temperature=0)
    message_texts = [msg['user'] + ": " + msg["text"] for msg in raw_conv]
    docs = [Document(page_content=text) for text in message_texts]

    prompt = """
    Write a concise summary of the following. Highlight clearly what was said, and by whom.
    "{text}"
    CONCISE SUMMARY:
    """
    prompt_template = PromptTemplate(template=prompt, input_variables=["text"])

    summarize_chain = load_summarize_chain(llm, chain_type="stuff", prompt=prompt_template)
    summary = summarize_chain.run(docs)
    return summary

async def get_slack_email(user_id):
    """
    Fetch data from the linear API based on the query string queryStr
    """
    try:
        slack_token = os.getenv("SLACK_API_TOKEN")
        if not slack_token:
            return {"status": 400, "error": "No slack API token found"}

        # Create a client instance
        client = WebClient(token=slack_token)

        # Specify the channel to fetch conversations from

        try:
            # Fetch conversations from the specified channel
            result = client.users_info(user=user_id)
        except SlackApiError as e:
            print(f"Error: {e.response['error']}")
            exit(1)

        return result['user']['profile']['email']

    except Exception as ex:
        print(ex)
        return None

async def get_slack_data(channel):
    """
    Fetch data from the linear API based on the query string queryStr
    """
    try:
        slack_token = os.getenv("SLACK_API_TOKEN")
        if not slack_token:
            return {"status": 400, "error": "No slack API token found"}

        # Create a client instance
        client = WebClient(token=slack_token)

        # Specify the channel to fetch conversations from

        try:
            # Fetch conversations from the specified channel
            result = client.conversations_history(channel=channel)
        except SlackApiError as e:
            print(f"Error: {e.response['error']}")
            exit(1)

        try:
            # Fetch conversations from the specified channel
            result = client.conversations_history(channel=channel)
        except SlackApiError as e:
            print(f"Error: {e.response['error']}")
            exit(1)

        # Create a list to hold the processed conversations
        processed_conversations = []

        # Iterate over each message in the channel's history
        for message in result["messages"]:
            # Create a list to hold the raw messages of this conversation
            raw_messages = []

            # Transform the message into a raw message dictionary and add it to the list
            raw_message = {
                # Use the timestamp as a unique ID
                "id": int(message["ts"].replace(".", "")),
                "text": message["text"],
                "time": datetime.datetime.fromtimestamp(float(message["ts"])),
                "user": message["user"],
                "userId": message["user"],  # Assume user ID is like 'U12345'
            }
            raw_messages.append(raw_message)

            # Initialize the conversation's end time with the message's timestamp
            end_time = datetime.datetime.fromtimestamp(float(message["ts"]))

            # If the message has replies, fetch them and update the conversation's end time
            if "thread_ts" in message:
                thread_result = client.conversations_replies(
                    channel=channel, ts=message["thread_ts"])
                for reply in thread_result["messages"]:
                    if reply["ts"] == message["ts"]:
                        continue  # Skip the message itself

                    # Transform each reply into a raw message dictionary and add it to the list
                    reply_raw_message = {
                        # Use the timestamp as a unique ID
                        "id": int(reply["ts"].replace(".", "")),
                        "text": reply["text"],
                        "time": datetime.datetime.fromtimestamp(float(reply["ts"])),
                        "user": reply["user"],
                        # Assume user ID is like 'U12345'
                        "userId": reply["user"],
                    }
                    raw_messages.append(reply_raw_message)

                    # Update the conversation's end time with the reply's timestamp
                    end_time = datetime.datetime.fromtimestamp(
                        float(reply["ts"]))

            # Summarize the conversation
            summary = summarize_conversation(raw_messages)
            print(summary)

            # Transform the thread into a processed conversation dictionary
            processed_conversation = {
                # Use the timestamp as a unique ID
                "id": int(message["ts"].replace(".", "")),
                "summary": summary,  # You need to implement how to generate a summary
                "startTime": datetime.datetime.fromtimestamp(float(message["ts"])),
                "endTime": end_time,
                "rawMsgs": raw_messages,
                "users": list(set([raw_message["user"] for raw_message in raw_messages])),
                # Assume user ID is like 'U12345'
                "userIds": list(set([raw_message["userId"] for raw_message in raw_messages])),
            }
            processed_conversations.append(processed_conversation)

        data = {'processed_conversations':processed_conversations}
        data['status'] = 200
        return data

    except Exception as ex:
        # print line number
        print(ex)
        return {"status": 400, "error": "Slack API call failed"}