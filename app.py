from flask import Flask, render_template, request, redirect, session, flash
from db import get_connection
import pandas as pd

app = Flask(__name__)
app.secret_key = "mysecret123"


@app.route('/')
def home():
    return redirect('/login')


# SIGNUP
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (name,email,password) VALUES (%s,%s,%s)",
                (name, email, password)
            )
            conn.commit()
            conn.close()

            flash("Signup successful! Please login.")
            return redirect('/login')

        except:
            conn.close()
            flash("Email already exists! Try another one.")

            return redirect('/signup')

    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():

    conn = get_connection()

    expense_df = pd.read_sql(
        "SELECT * FROM expense WHERE user_id=%s",
        conn,
        params=[session['user_id']]
    )

    income_df = pd.read_sql(
        "SELECT * FROM income WHERE user_id=%s",
        conn,
        params=[session['user_id']]
    )

    total_expense = expense_df['amount'].sum() if not expense_df.empty else 0
    total_income = income_df['amount'].sum() if not income_df.empty else 0

    balance = total_income - total_expense

    category_summary = {}

    if not expense_df.empty:
        category_summary = (
            expense_df.groupby('category')['amount']
            .sum()
            .to_dict()
        )

    recent_expenses = []

    if not expense_df.empty:
        recent_expenses = (
            expense_df.sort_values(
                by='date',
                ascending=False
            )
            .head(5)
            .to_dict('records')
        )

    conn.close()

    return render_template(
        'dashboard.html',
        total_income=total_income,
        total_expense=total_expense,
        balance=balance,
        category_summary=category_summary,
        recent_expenses=recent_expenses
    )
# LOGIN PAGE
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s",
                       (email, password))
        user = cursor.fetchone()

        if user:
            session['user_id'] = user[0]
            return redirect('/dashboard')

    return render_template('login.html')

# EXPENSE PAGE
@app.route('/expense', methods=['GET', 'POST'])
def expense():
    if request.method == 'POST':
        amount = request.form['amount']
        category = request.form['category']
        date = request.form['date']
        description = request.form['description']

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO expense (user_id, amount, category, date, description) VALUES (%s,%s,%s,%s,%s)",
            (session['user_id'], amount, category, date, description)
        )

        conn.commit()
        conn.close()

        return redirect('/dashboard')

    return render_template('expense.html')

# INCOME PAGE
@app.route("/income")
def income_page():
    return render_template("income.html")


# ADD EXPENSE
@app.route('/add_expense', methods=['POST'])
def add_expense():

    user_id = session['user_id']
    amount = request.form['amount']
    category = request.form['category']
    date = request.form['date']
    description = request.form['description']

    conn = get_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO expense
    (user_id, amount, category, date, description)
    VALUES (%s,%s,%s,%s,%s)
    """

    cursor.execute(
        query,
        (
            user_id,
            amount,
            category,
            date,
            description
        )
    )

    conn.commit()
    conn.close()

    return redirect('/dashboard')


# ADD INCOME
@app.route('/add_income', methods=['POST'])
def add_income():

    user_id = session['user_id']
    amount = request.form['amount']
    source = request.form['source']
    date = request.form['date']

    conn = get_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO income
    (user_id, amount, source, date)
    VALUES (%s,%s,%s,%s)
    """

    cursor.execute(
        query,
        (user_id, amount, source, date)
    )

    conn.commit()
    conn.close()

    return redirect('/dashboard')


# ANALYTICS
@app.route("/analytics")
def analytics():

    conn = get_connection()

    df = pd.read_sql(
        "SELECT * FROM expense",
        conn
    )

    total_expense = df["amount"].sum()

    conn.close()

    return f"Total Expense: {total_expense}"


# RUN SERVER (ALWAYS LAST)
if __name__ == "__main__":
    app.run(debug=True)