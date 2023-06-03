import io
from fastapi import FastAPI, UploadFile, File, HTTPException
from preprocessing import return_relevant_document_context
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sources.slack import get_slack_data
from dotenv import load_dotenv
from prisma import Prisma
from sources.linear import get_linear_data
from sources.db_utils import connect_db
from utils.classifier import get_conv_classification
from datetime import datetime
from views.graphs import view_time_conversations, dummy_conversations
import json

load_dotenv()


app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://localhost:*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CompletionRequestBody(BaseModel):
    context: str


def extract_stream(file: UploadFile = File(...)):
    pdf_as_bytes = file.file.read()
    # We convert the bytes into a Streamable object of bytes
    return io.BytesIO(pdf_as_bytes)


@app.get("/")
async def root():
    try:
        db = Prisma()
        await db.connect()
        # post = await db.user.create({})

        return {"hello": "world"}
    except Exception as ex:
        print(ex)
        return {"error": "yes"}


def parse_processed_conversation(conv):
    """
    Parse a processed conversation object from the database into a dictionary
    """
    return {
        "id": conv.id,
        "summary": conv.summary,
        "embedding": json.loads(conv.embedding),
        "startTime": conv.startTime.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "endTime": conv.endTime.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
    }


@app.get("/time")
async def time():
    try:
        view_time_conversations(dummy_conversations)
    except Exception as ex:
        print(ex)
        raise ex


@app.get("/user")
async def get_user(id: str):
    try:
        db = await connect_db()
        user = await db.user.find_first(where={"id": int(id)})
        # get user embeddings

        # fetch all processed conversations a user is part of
        # make a db query to get all raw messages for a user given their id and include the processed conversations as well as the embeddings under processed conversations
        raw_messages = await db.rawmessage.find_many(where={"userId": int(id)}, include={"processedConversations": True})
        processed_conversations = list(map(
            lambda msg: parse_processed_conversation(msg.processedConversations), raw_messages))

        # write processed_converstations to a file
        # with open('./processed_conversations.json', 'w') as f:
        #     json.dump(processed_conversations, f)

        # compute similarity between user embeddings and all other user embeddings

        # find the top n most similar other embeddings / cluster

        # apply tsne to reduce the dimensionality

        # get labels for the cluster

        # return data to frontend and visualize it
        return user
    except Exception as ex:
        print(ex)
        raise HTTPException(status_code=400, detail="Error getting user")


@app.get("/users")
async def get_users():
    try:
        db = await connect_db()
        users = await db.user.find_many()
        return users
    except Exception as ex:
        print(ex)
        raise HTTPException(status_code=400, detail="Error getting users")


@app.get("/slack")
async def slack():
    try:
        data = await get_slack_data()
        return data
    except Exception as ex:
        print(ex)
        raise HTTPException(status_code=400, detail="Slack API call failed")


@app.get("/linear")
async def linear():
    """
    Fetch data from the linear API, write users and tickets.
    """
    async def add_users_to_db_from_issues(db, issues):
        """
        Given a list of issues from Linear, add all users to the database
        that are not already in the database.
        """
        for issue in issues:
            if 'assignee' in issue and issue['assignee']:
                assignee = issue['assignee']
                try:
                    # We haven't seen this linear user before
                    userByLinearId = await db.user.find_first(where={"linearId": assignee['id']})
                    # We haven't seen this slack user (same email) before
                    userByEmail = await db.user.find_first(where={"email": assignee['email']})
                    if not userByLinearId and not userByEmail:
                        user = await db.user.create({"linearId": assignee['id'], "name": assignee['name'], 'email': assignee['email']})
                except Exception as ex:
                    print(ex)
                    return {"status": 400, "error": f"User creation failed {assignee['id']}"}
        return {"status": 200, "success": True, "message": "Users added to database"}

    async def add_projects_to_db(db, issues):
        """
        Given a list of issues from Linear, add all projects to the database
        """
        for issue in issues:
            if 'project' in issue and issue['project']:
                project = issue['project']
                try:
                    # We haven't seen this project before
                    projectStr = project['name']
                    projectByStr = await db.project.find_first(where={'name': projectStr})
                    if not projectByStr:
                        project = await db.project.create({"name": projectStr})
                except Exception as ex:
                    print(ex)
                    return {"status": 400, "error": f"Project creation failed {projectStr}"}
        return {"status": 200, "success": True, "message": "Projects added to database"}

    async def get_user_from_issue(db, issue):
        """
        Given an issue from Linear, get the database user id for the linear id
        """
        # Get the database user id for the linear id
        if 'assignee' in issue and issue['assignee']:
            assignee = issue['assignee']
            user = await db.user.find_first(where={"linearId": assignee['id']})
        else:
            user = None
        return user

    async def get_project_from_issue(db, issue):
        """
        Given an issue from Linear, get the project name
        """
        if 'project' in issue and issue['project']:
            project = issue['project']
            projectStr = project['name']
            dbProject = await db.project.find_first(where={'name': projectStr})
            if dbProject:
                return dbProject
        return None

    async def add_ticket_to_user(ticket, user):
        """
        Given a ticket and a user, add the ticket to the user's tickets
        """
        if user:
            await db.user.update(where={"id": user.id}, data={"tickets": {"connect": {"id": ticket.id}}})

    async def add_ticket_to_project(ticket, project):
        """
        Given a ticket and a project, add the ticket to the project's tickets
        """
        if project:
            await db.project.update(where={"id": project.id}, data={"tickets": {"connect": {"id": ticket.id}}})

    async def add_project_to_user(project, user):
        """
        Given a project and a user, add the project to the user's projects
        """
        if user and project:
            await db.user.update(where={"id": user.id}, data={"projects": {"connect": {"id": project.id}}})

    db = await connect_db()
    if not db:
        return {"status": 400, "error": "Database connection failed"}

    data = get_linear_data()
    # do all sanity checks
    if data['status'] != 200:
        return data

    # get all issues
    issues = data['data']['issues']['nodes']

    # For every issue, check if the assignee exists in the database.
    # If not, create a new user.
    response = await add_users_to_db_from_issues(db, issues)
    if response['status'] != 200:
        return response

    response = await add_projects_to_db(db, issues)
    if response['status'] != 200:
        return response

    # add all issues to the database
    for issue in issues:
        try:
            # If ticket with linearId already exists, skip
            ticket = await db.ticket.find_first(where={"linearId": issue['id']})
            if ticket:
                continue

            user = await get_user_from_issue(db, issue)
            project = await get_project_from_issue(db, issue)
            await add_project_to_user(project, user)

            projectId = project.id if project else None

            query = {
                "linearId": issue['id'],
                "title": issue['title'],
                "description": issue['description'],
                "createdAt": datetime.strptime(issue['createdAt'], "%Y-%m-%dT%H:%M:%S.%fZ"),
            }
            if projectId is not None:
                query['projectId'] = projectId
            if user is not None:
                query['userId'] = user.id

            # Create the issue
            ticket = await db.ticket.create(query)
            await add_ticket_to_user(ticket, user)
            await add_ticket_to_project(ticket, project)

        except Exception as ex:
            print(ex)
            return {"status": 400, "error": f"Issue creation failed {issue['id']}"}

    return {"status": 200, "success": True, "message": "Issues added to database"}


@app.get("/map-slack-to-linear")
async def map_slack_to_linear():
    async def get_project_for_conv(conversation, projects):
        """
        Given a conversation, get the project it belongs to
        """
        convStr = conversation.summary
        projNames = [proj.name for proj in projects]
        projClassName = get_conv_classification(convStr, projNames).strip()
        if projClassName == "None":
            return None
        else:
            # Get the project for projects with the name projClassName
            project = None
            for proj in projects:
                if proj.name == projClassName:
                    project = proj
                    break
            return project

    # Get all users from the database
    db = await connect_db()
    if not db:
        return {"status": 400, "error": "Database connection failed"}

    users = await db.user.find_many()
    projects = await db.project.find_many()
    for user in users:
        # Get all their conversations
        conversations = await db.processedconversation.find_many(where={"userId": user.id})
        for conversation in conversations:
            classified_proj = await get_project_for_conv(conversation, projects)
            if classified_proj:
                await db.processedconversation.update(where={"id": conversation.id}, data={"projectId": classified_proj.id})
                await db.project.update(where={"id": classified_proj.id}, data={"processedConversations": {"connect": {"id": conversation.id}}})
