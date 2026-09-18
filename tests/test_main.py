from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "DevOps Inventory API is running"
    }


@patch("app.main.psycopg.connect")
def test_get_inventory(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.fetchall.return_value = [
        (1, "Laptop", "Electronics", 10, 8500000.00),
        (2, "Keyboard", "Accessories", 25, 350000.00),
    ]

    response = client.get("/inventory")

    assert response.status_code == 200

    assert response.json() == [
        {
            "id": 1,
            "name": "Laptop",
            "category": "Electronics",
            "quantity": 10,
            "price": 8500000.0,
        },
        {
            "id": 2,
            "name": "Keyboard",
            "category": "Accessories",
            "quantity": 25,
            "price": 350000.0,
        },
    ]


@patch("app.main.psycopg.connect")
def test_create_inventory(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.fetchone.return_value = (
        4,
        "Mouse",
        "Accessories",
        20,
        150000.00,
    )

    response = client.post(
        "/inventory",
        json={
            "name": "Mouse",
            "category": "Accessories",
            "quantity": 20,
            "price": 150000,
        },
    )

    assert response.status_code == 200

    assert response.json() == {
        "id": 4,
        "name": "Mouse",
        "category": "Accessories",
        "quantity": 20,
        "price": 150000.0,
    }

    mock_conn.commit.assert_called_once()


@patch("app.main.psycopg.connect")
def test_update_inventory(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.fetchone.return_value = (
        4,
        "Mouse",
        "Accessories",
        50,
        175000.00,
    )

    response = client.put(
        "/inventory/4",
        json={
            "name": "Mouse",
            "category": "Accessories",
            "quantity": 50,
            "price": 175000,
        },
    )

    assert response.status_code == 200

    assert response.json() == {
        "id": 4,
        "name": "Mouse",
        "category": "Accessories",
        "quantity": 50,
        "price": 175000.0,
    }

    mock_conn.commit.assert_called_once()


@patch("app.main.psycopg.connect")
def test_delete_inventory(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.fetchone.return_value = (4,)

    response = client.delete("/inventory/4")

    assert response.status_code == 200

    assert response.json() == {
        "message": "Inventory item deleted",
        "id": 4,
    }

    mock_conn.commit.assert_called_once()


@patch("app.main.psycopg.connect")
def test_update_inventory_not_found(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.fetchone.return_value = None

    response = client.put(
        "/inventory/999",
        json={
            "name": "Mouse",
            "category": "Accessories",
            "quantity": 50,
            "price": 175000,
        },
    )

    assert response.status_code == 200

    assert response.json() == {
        "error": "Inventory item not found"
    }

    mock_conn.commit.assert_not_called()


@patch("app.main.psycopg.connect")
def test_delete_inventory_not_found(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.fetchone.return_value = None

    response = client.delete("/inventory/999")

    assert response.status_code == 200

    assert response.json() == {
        "error": "Inventory item not found"
    }

    mock_conn.commit.assert_not_called()
