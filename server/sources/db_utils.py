from prisma import Prisma


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
