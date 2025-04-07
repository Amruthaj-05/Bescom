
# app.py
from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "supersecret"
DB = "users.db"

# Initialize DB with user and bill tables
def init_db():
    with sqlite3.connect(DB) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                address TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS bills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id TEXT NOT NULL,
                amount REAL NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('Paid', 'Unpaid')),
                FOREIGN KEY (customer_id) REFERENCES users(customer_id)
            );
        """)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    customer_id = request.form["customer_id"]
    with sqlite3.connect(DB) as conn:
        user = conn.execute("SELECT * FROM users WHERE customer_id = ?", (customer_id,)).fetchone()
    if user:
        session["customer_id"] = customer_id
        return redirect("/dashboard")
    return "Customer ID not found. <a href='/'>Try again</a>"

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        customer_id = request.form["customer_id"]
        name = request.form["name"]
        address = request.form["address"]
        phone = request.form["phone"]
        email = request.form["email"]

        with sqlite3.connect(DB) as conn:
            try:
                conn.execute("""
                    INSERT INTO users (customer_id, name, address, phone, email)
                    VALUES (?, ?, ?, ?, ?)
                """, (customer_id, name, address, phone, email))

                # Optional: Add a sample unpaid bill
                conn.execute("INSERT INTO bills (customer_id, amount, status) VALUES (?, ?, ?)",
                             (customer_id, 850.00, "Unpaid"))

                return redirect("/")
            except sqlite3.IntegrityError:
                return "Customer ID already exists. <a href='/register'>Try again</a>"

    return render_template("register.html")

@app.route("/dashboard")
def dashboard():
    if "customer_id" not in session:
        return redirect("/")

    customer_id = session["customer_id"]
    with sqlite3.connect(DB) as conn:
        user = conn.execute("SELECT name, address, email FROM users WHERE customer_id = ?", (customer_id,)).fetchone()
        bill = conn.execute("SELECT amount, status FROM bills WHERE customer_id = ?", (customer_id,)).fetchone()

    if user and bill:
        name, address, email = user
        amount, status = bill
        return render_template("dashboard.html",
                               customer_id=customer_id,
                               name=name,
                               address=address,
                               email=email,
                               amount=amount,
                               status=status)

    return "Data not found"

if __name__ == "__main__":
    init_db()
    app.run(debug=True)