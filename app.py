from flask import Flask, render_template, request, redirect
import sqlite3
from collections import defaultdict

app = Flask(__name__)


def get_db():
    connection = sqlite3.connect("expenses.db")
    connection.row_factory = sqlite3.Row
    return connection


def create_table():

    connection = get_db()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            date TEXT
        )
    """)

    columns = connection.execute(
        "PRAGMA table_info(expenses)"
    ).fetchall()

    column_names = [column["name"] for column in columns]

    if "date" not in column_names:
        connection.execute(
            "ALTER TABLE expenses ADD COLUMN date TEXT"
        )

    connection.commit()
    connection.close()


@app.route("/", methods=["GET", "POST"])
def home():

    connection = get_db()

    if request.method == "POST":

        amount = request.form["amount"]
        category = request.form["category"]
        description = request.form["description"]
        date = request.form["date"]

        connection.execute(
            """
            INSERT INTO expenses
            (amount, category, description, date)
            VALUES (?, ?, ?, ?)
            """,
            (amount, category, description, date)
        )

        connection.commit()

    expenses = connection.execute(
        "SELECT * FROM expenses"
    ).fetchall()

    connection.close()

    total = sum(expense["amount"] for expense in expenses)

    category_totals = defaultdict(float)

    for expense in expenses:
        category_totals[expense["category"]] += expense["amount"]

    return render_template(
        "index.html",
        expenses=expenses,
        total=total,
        category_totals=dict(category_totals)
    )


@app.route("/delete/<int:id>")
def delete(id):

    connection = get_db()

    connection.execute(
        "DELETE FROM expenses WHERE id = ?",
        (id,)
    )

    connection.commit()
    connection.close()

    return redirect("/")


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):

    connection = get_db()

    if request.method == "POST":

        amount = request.form["amount"]
        category = request.form["category"]
        description = request.form["description"]
        date = request.form["date"]

        connection.execute(
            """
            UPDATE expenses
            SET amount = ?, category = ?, description = ?, date = ?
            WHERE id = ?
            """,
            (amount, category, description, date, id)
        )

        connection.commit()
        connection.close()

        return redirect("/")

    expense = connection.execute(
        "SELECT * FROM expenses WHERE id = ?",
        (id,)
    ).fetchone()

    connection.close()

    return render_template(
        "edit.html",
        expense=expense
    )


create_table()

if __name__ == "__main__":
    app.run(debug=True)