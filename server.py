import sqlite3
import argparse
from mcp.server.fastmcp import FastMCP

mcp = FastMCP('sqlite-demo')

# Init database and create table if not exists
def init_db():
    conn = sqlite3.connect('demo.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS people (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            profession TEXT NOT NULL
        )
    ''')
    conn.commit()
    return conn, cursor

@mcp.tool()
def add_data(name: str, age: int, profession: str) -> bool:
    """
    Add a person to the people table.

    Args:
        name (str): Name of the person
        age (int): Age of the person
        profession (str): Job/profession

    Returns:
        bool: True if insert successful
    """
    conn, cursor = init_db()
    try:
        cursor.execute(
            "INSERT INTO people (name, age, profession) VALUES (?, ?, ?)",
            (name, age, profession)
        )
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error adding data: {e}")
        return False
    finally:
        conn.close()

@mcp.tool()
def read_data(query: str = "SELECT * FROM people") -> list:
    """Read data from the people table using a SQL SELECT query."""
    conn, cursor = init_db()
    try:
        cursor.execute(query)
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error reading data: {e}")
        return []
    finally:
        conn.close()

@mcp.tool()
def update_data(name: str, age: int = None, profession: str = None) -> bool:
    """
    Update existing data in the people table by name.

    Args:
        name (str): Name of the person to update
        age (int, optional): New age
        profession (str, optional): New profession

    Returns:
        bool: True if update was successful, False otherwise.
    """
    if age is None and profession is None:
        print("No fields to update")
        return False

    conn, cursor = init_db()
    try:
        updates = []
        values = []

        if age is not None:
            updates.append("age = ?")
            values.append(age)
        if profession is not None:
            updates.append("profession = ?")
            values.append(profession)

        values.append(name)

        sql = f"UPDATE people SET {', '.join(updates)} WHERE name = ?"
        cursor.execute(sql, tuple(values))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error updating data: {e}")
        return False
    finally:
        conn.close()

@mcp.tool()
def delete_data(name: str) -> bool:
    """
    Delete a person from the people table by name.

    Args:
        name (str): Name of the person to delete

    Returns:
        bool: True if deletion was successful, False otherwise.
    """
    conn, cursor = init_db()
    try:
        cursor.execute("DELETE FROM people WHERE name = ?", (name,))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error deleting data: {e}")
        return False
    finally:
        conn.close()


if __name__ == "__main__":
    print("🚀 Starting MCP SQLite Server...")
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--server_type", type=str, default="sse", choices=["sse", "stdio"]
    )
    args = parser.parse_args()
    mcp.run(args.server_type)
