import os

import psycopg
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "inventory")
DB_PASSWORD = os.getenv("DB_PASSWORD", "inventory123")
DB_NAME = os.getenv("DB_NAME", "inventory")


class InventoryItem(BaseModel):
    name: str
    category: str
    quantity: int
    price: float


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


@app.get("/inventory")
def get_inventory():
    conn = psycopg.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname=DB_NAME,
    )

    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, name, category, quantity, price "
        "FROM inventory ORDER BY id;"
    )

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return [
        {
            "id": row[0],
            "name": row[1],
            "category": row[2],
            "quantity": row[3],
            "price": float(row[4]),
        }
        for row in rows
    ]


@app.post("/inventory")
def create_inventory(item: InventoryItem):
    conn = psycopg.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname=DB_NAME,
    )

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO inventory (name, category, quantity, price)
        VALUES (%s, %s, %s, %s)
        RETURNING id, name, category, quantity, price;
        """,
        (item.name, item.category, item.quantity, item.price),
    )

    row = cursor.fetchone()

    conn.commit()

    cursor.close()
    conn.close()

    return {
        "id": row[0],
        "name": row[1],
        "category": row[2],
        "quantity": row[3],
        "price": float(row[4]),
    }

@app.put("/inventory/{item_id}")
def update_inventory(item_id: int, item: InventoryItem):
    conn = psycopg.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname=DB_NAME,
    )

    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE inventory
        SET name = %s,
            category = %s,
            quantity = %s,
            price = %s
        WHERE id = %s
        RETURNING id, name, category, quantity, price;
        """,
        (
            item.name,
            item.category,
            item.quantity,
            item.price,
            item_id,
        ),
    )

    row = cursor.fetchone()

    if row is None:
        cursor.close()
        conn.close()
        return {"error": "Inventory item not found"}

    conn.commit()

    cursor.close()
    conn.close()

    return {
        "id": row[0],
        "name": row[1],
        "category": row[2],
        "quantity": row[3],
        "price": float(row[4]),
    }

@app.delete("/inventory/{item_id}")
def delete_inventory(item_id: int):
    conn = psycopg.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname=DB_NAME,
    )

    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM inventory
        WHERE id = %s
        RETURNING id;
        """,
        (item_id,),
    )

    row = cursor.fetchone()

    if row is None:
        cursor.close()
        conn.close()
        return {"error": "Inventory item not found"}

    conn.commit()

    cursor.close()
    conn.close()

    return {
        "message": "Inventory item deleted",
        "id": row[0],
    }