from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Database setup
def init_db():
    conn = sqlite3.connect('budgeting.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    description TEXT NOT NULL,
                    amount REAL NOT NULL,
                    date TEXT NOT NULL
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS achievements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    unlocked INTEGER DEFAULT 0
                )''')
    conn.commit()
    conn.close()

# Populate achievements
def init_achievements():
    conn = sqlite3.connect('budgeting.db')
    c = conn.cursor()
    achievements = [
        ("First Transaction", 0),
        ("Saved $100", 0),
        ("Saved $500", 0),
        ("Logged 10 Transactions", 0)
    ]
    c.executemany('INSERT OR IGNORE INTO achievements (name, unlocked) VALUES (?, ?)', achievements)
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = sqlite3.connect('budgeting.db')
    c = conn.cursor()

    # Get all transactions
    c.execute('SELECT * FROM transactions ORDER BY date DESC')
    transactions = c.fetchall()

    # Calculate total savings
    c.execute('SELECT SUM(amount) FROM transactions WHERE amount > 0')
    total_savings = c.fetchone()[0] or 0

    # Update achievements
    if total_savings >= 100:
        c.execute('UPDATE achievements SET unlocked = 1 WHERE name = "Saved $100"')
    if total_savings >= 500:
        c.execute('UPDATE achievements SET unlocked = 1 WHERE name = "Saved $500"')
    c.execute('SELECT COUNT(*) FROM transactions')
    if c.fetchone()[0] >= 10:
        c.execute('UPDATE achievements SET unlocked = 1 WHERE name = "Logged 10 Transactions"')
    conn.commit()

    # Get achievements
    c.execute('SELECT * FROM achievements')
    achievements = c.fetchall()

    conn.close()
    return render_template('index.html', transactions=transactions, total_savings=total_savings, achievements=achievements)

@app.route('/add', methods=['POST'])
def add_transaction():
    description = request.form['description']
    amount = float(request.form['amount'])
    date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    conn = sqlite3.connect('budgeting.db')
    c = conn.cursor()
    c.execute('INSERT INTO transactions (description, amount, date) VALUES (?, ?, ?)', (description, amount, date))
    c.execute('UPDATE achievements SET unlocked = 1 WHERE name = "First Transaction"')
    conn.commit()
    conn.close()

    return redirect(url_for('index'))

@app.route('/delete/<int:transaction_id>')
def delete_transaction(transaction_id):
    conn = sqlite3.connect('budgeting.db')
    c = conn.cursor()
    c.execute('DELETE FROM transactions WHERE id = ?', (transaction_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    init_achievements()
    app.run(debug=True)
