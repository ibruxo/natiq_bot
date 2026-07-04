from sqlalchemy import text

from db.session import engine

print("Connecting...")

with engine.connect() as conn:
    result = conn.execute(text("SELECT 1"))

    print(result.scalar())

print("Success!")
