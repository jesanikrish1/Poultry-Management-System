from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os

app = Flask(__name__)

app.secret_key = "poultry_farm_secret_key_2024"

DATABASE = "poultry.db"

def get_db():
    """Open a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE)
    # Return rows as dictionary-like objects (accessible by column name)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Create tables if they don't already exist."""
    conn = get_db()
    cursor = conn.cursor()

    # Create batches table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS batches (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            breed    TEXT    NOT NULL,
            quantity INTEGER NOT NULL,
            age      INTEGER NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS eggs (
            id    INTEGER PRIMARY KEY AUTOINCREMENT,
            date  TEXT    NOT NULL,
            count INTEGER NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feed (
            id     INTEGER PRIMARY KEY AUTOINCREMENT,
            date   TEXT    NOT NULL,
            amount REAL    NOT NULL
        )
    """)

    conn.commit()
    conn.close()

@app.route("/")
def index():
    """
    Display the main dashboard with all stored records.
    Fetches data from all three tables and passes them to the template.
    """
    conn = get_db()

    batches = conn.execute("SELECT * FROM batches ORDER BY id DESC").fetchall()
    eggs    = conn.execute("SELECT * FROM eggs    ORDER BY id DESC").fetchall()
    feeds   = conn.execute("SELECT * FROM feed    ORDER BY id DESC").fetchall()

    # Summary counts for the stats cards
    total_batches  = conn.execute("SELECT COUNT(*) FROM batches").fetchone()[0]
    total_birds    = conn.execute("SELECT SUM(quantity) FROM batches").fetchone()[0] or 0
    total_eggs     = conn.execute("SELECT SUM(count) FROM eggs").fetchone()[0] or 0
    total_feed     = conn.execute("SELECT SUM(amount) FROM feed").fetchone()[0] or 0.0

    conn.close()

    return render_template(
        "index.html",
        batches=batches,
        eggs=eggs,
        feeds=feeds,
        total_batches=total_batches,
        total_birds=total_birds,
        total_eggs=total_eggs,
        total_feed=round(total_feed, 2),
    )

@app.route("/add_batch", methods=["POST"])
def add_batch():
    """
    Handle the 'Add Batch' form submission.
    Validates the input, then inserts a new record into the batches table.
    """
    breed    = request.form.get("breed", "").strip()
    quantity = request.form.get("quantity", "").strip()
    age      = request.form.get("age", "").strip()

    if not breed:
        flash("Breed name is required.", "error")
        return redirect(url_for("index") + "#batch-section")

    if not quantity.isdigit() or int(quantity) <= 0:
        flash("Quantity must be a positive whole number.", "error")
        return redirect(url_for("index") + "#batch-section")

    if not age.isdigit() or int(age) < 0:
        flash("Age must be zero or a positive whole number (in weeks).", "error")
        return redirect(url_for("index") + "#batch-section")

    conn = get_db()
    conn.execute(
        "INSERT INTO batches (breed, quantity, age) VALUES (?, ?, ?)",
        (breed, int(quantity), int(age))
    )
    conn.commit()
    conn.close()

    flash(f"Batch '{breed}' added successfully!", "success")
    return redirect(url_for("index"))

@app.route("/add_egg", methods=["POST"])
def add_egg():
    """
    Handle the 'Add Egg Record' form submission.
    Validates the input, then inserts a new record into the eggs table.
    """
    date  = request.form.get("date", "").strip()
    count = request.form.get("count", "").strip()

    if not date:
        flash("Date is required for egg record.", "error")
        return redirect(url_for("index") + "#egg-section")

    if not count.isdigit() or int(count) < 0:
        flash("Egg count must be zero or a positive whole number.", "error")
        return redirect(url_for("index") + "#egg-section")

    conn = get_db()
    conn.execute(
        "INSERT INTO eggs (date, count) VALUES (?, ?)",
        (date, int(count))
    )
    conn.commit()
    conn.close()

    flash(f"Egg record for {date} added successfully!", "success")
    return redirect(url_for("index"))

@app.route("/add_feed", methods=["POST"])
def add_feed():
    """
    Handle the 'Add Feed Record' form submission.
    Validates the input, then inserts a new record into the feed table.
    """
    date   = request.form.get("date", "").strip()
    amount = request.form.get("amount", "").strip()

    if not date:
        flash("Date is required for feed record.", "error")
        return redirect(url_for("index") + "#feed-section")

    try:
        amount_float = float(amount)
        if amount_float <= 0:
            raise ValueError
    except ValueError:
        flash("Feed amount must be a positive number (e.g. 12.5 kg).", "error")
        return redirect(url_for("index") + "#feed-section")

    conn = get_db()
    conn.execute(
        "INSERT INTO feed (date, amount) VALUES (?, ?)",
        (date, amount_float)
    )
    conn.commit()
    conn.close()

    flash(f"Feed record for {date} added successfully!", "success")
    return redirect(url_for("index"))

@app.route("/delete/<table>/<int:record_id>", methods=["POST"])
def delete_record(table, record_id):
    """
    Delete a single record from the given table.
    Only allows deleting from known tables (safety check).
    """
    allowed_tables = {"batches", "eggs", "feed"}
    if table not in allowed_tables:
        flash("Invalid table specified.", "error")
        return redirect(url_for("index"))

    conn = get_db()
    conn.execute(f"DELETE FROM {table} WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()

    flash("Record deleted successfully.", "success")
    return redirect(url_for("index"))

if __name__ == "__main__":
    init_db()
    print("=" * 50)
    print("  Poultry Farm Management System")
    print("  Running at: http://127.0.0.1:5000")
    print("=" * 50)
    app.run(debug=True)
