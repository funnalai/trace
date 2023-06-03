import datetime
import os
from fastapi import HTTPException, status
from sources.db_utils import connect_db
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

    summarize_chain = load_summarize_chain(
        llm, chain_type="stuff", prompt=prompt_template)
    summary = summarize_chain.run(docs)
    return summary


async def get_slack_profile(user_id, client):
    """
    Fetch data from the linear API based on the query string queryStr
    """
    try:
        slack_token = os.getenv("SLACK_API_TOKEN")
        if not slack_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="No slack API token found")

        try:
            # Fetch conversations from the specified channel
            result = client.users_info(user=user_id)
        except SlackApiError as e:
            print(f"Error: {e.response['error']}")
            exit(1)

        return result['user']['profile']

    except Exception as ex:
        print(ex)
        raise ex


async def get_slack_data(channel):
    """
    Fetch data from the slack API based on the query string queryStr
    """
    try:
        db = await connect_db()
        if not db:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Database connection failed")

        slack_token = os.getenv("SLACK_API_TOKEN")
        if not slack_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No slack API token found",
            )

        # Create a client instance
        client = WebClient(token=slack_token)

        # Specify the channel to fetch conversations from
        try:
            # Fetch conversations from the specified channel
            result = client.conversations_history(channel=channel)
        except SlackApiError as e:
            print("Error fetching result for channel: ", e)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error: {e.response['error']}",
            )

        try:
            # Fetch conversations from the specified channel
            result = client.conversations_history(channel=channel)
        except SlackApiError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error: {e.response['error']}",
            )

        # Create a list to hold the processed conversations
        processed_conversations = []
        all_raw_messages = []

        # Iterate over each message in the channel's history
        for message in result["messages"]:
            # Create a list to hold the raw messages of this conversation
            raw_messages = []

            slack_user_id = str(message["user"].replace(".", ""))
            slack_profile = await get_slack_profile(user_id=slack_user_id, client=client)

            # check if user with slackId or email exists in database
            user = await db.user.find_first(where={"email": slack_profile["email"]})

            if not user:
                # create user
                user = await db.user.create({"slackId": slack_user_id, "email": slack_profile["email"], "name": slack_profile["real_name"]})
            elif not user.slackId:
                # update the record with slackId
                user = await db.user.update(where={"email": slack_profile["email"]}, data={"slackId": slack_user_id})

            print("user: ", user)
            break
            # Transform the message into a raw message dictionary and add it to the list
            raw_message = {
                # Use the timestamp as a unique ID
                "id": user["id"],
                "email": user["email"],
                "slackId": slack_user_id,
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
            # append all raw messages to all_row_messages
            all_raw_messages.extend(raw_messages)

        data = {
            "processed_conversations": processed_conversations,
            "raw_messages": all_raw_messages
        }

        # Write the processed conversation to the database
        return data

    except Exception as ex:
        # print line number
        print(ex)
        raise ex
