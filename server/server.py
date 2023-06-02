import io
from fastapi import FastAPI, UploadFile, File, HTTPException
from preprocessing import return_relevant_document_context
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from prisma import Prisma
from sources.linear import get_linear_data
from datetime import datetime

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

async def connect_db():
    """
    Connect to the database. Returns None if connection fails.
    """
    try:
        db = Prisma()
        await db.connect()
        return db
    except Exception as ex:
        print(ex)
        return None

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
                    user = await db.user.find_first(where={"linearId": assignee['id']})
                    if not user:
                        user = await db.user.create({"linearId": assignee['id'], "name": assignee['name']})
                except Exception as ex:
                    print(ex)
                    return {"status": 400, "error": f"User creation failed {assignee['id']}"}
        return {"status": 200, "success": True, "message": "Users added to database"}

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
        else:
            projectStr = None
        return projectStr

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

    # add all issues to the database
    for issue in issues:
        try:
            # If ticket with linearId already exists, skip
            ticket = await db.ticket.find_first(where={"linearId": issue['id']})
            if ticket:
                continue

            user = await get_user_from_issue(db, issue)
            projectStr = await get_project_from_issue(db, issue)

            query = {
                    "linearId": issue['id'],
                    "title": issue['title'],
                    "description": issue['description'],
                    "createdAt": datetime.strptime(issue['createdAt'], "%Y-%m-%dT%H:%M:%S.%fZ"),
                    "projectStr": projectStr
                }
            if projectStr is not None: query['projectStr'] = projectStr
            if user is not None: query['userId'] = user.id

            # Create the issue
            await db.ticket.create(query)
        except Exception as ex:
            print(ex)
            return {"status": 400, "error": f"Issue creation failed {issue['id']}"}

    return {"status": 200, "success": True, "message": "Issues added to database"}


