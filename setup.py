import sqlite3
import os

DATABASE = "poultry.db"


def setup_database():
    """Create the poultry.db database and all required tables."""

    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    print(f"Setting up database: {os.path.abspath(DATABASE)}")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS batches (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            breed    TEXT    NOT NULL,
            quantity INTEGER NOT NULL,
            age      INTEGER NOT NULL
        )
    """)
    print("  [OK] Table 'batches' ready.")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS eggs (
            id    INTEGER PRIMARY KEY AUTOINCREMENT,
            date  TEXT    NOT NULL,
            count INTEGER NOT NULL
        )
    """)
    print("  [OK] Table 'eggs' ready.")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feed (
            id     INTEGER PRIMARY KEY AUTOINCREMENT,
            date   TEXT    NOT NULL,
            amount REAL    NOT NULL
        )
    """)
    print("  [OK] Table 'feed' ready.")

    conn.commit()
    conn.close()

    print("\nDatabase setup complete!")
    print("You can now run the app:  python app.py")


if __name__ == "__main__":
    setup_database()
