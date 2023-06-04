from prisma import Prisma
import json

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

async def create_slack_users(filename):
    with open(filename) as f:
        data = json.load(f)
        data = data['users']
    db = await connect_db()
    for user in data:
        if not user or 'name' not in user or 'email' not in user:
            continue
        created_user = await db.user.create({
                'name': user['name'],
                'email': user['email'],
            })
        if created_user:
            print(f"Created user {user['name']}")
        else:
            print(f"Failed to create user {user['name']}")


