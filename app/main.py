import os

import psycopg
from fastapi import FastAPI

app = FastAPI()


DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "inventory")
DB_PASSWORD = os.getenv("DB_PASSWORD", "inventory123")
DB_NAME = os.getenv("DB_NAME", "inventory")


@app.get("/")
def root():
    return {"message": "DevOps Inventory API is running"}


@app.get("/db-test")
def db_test():
    conn = psycopg.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname=DB_NAME,
    )

    cursor = conn.cursor()
    cursor.execute("SELECT 1;")
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return {
        "database": "connected",
        "result": result[0],
    }
