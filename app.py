from flask import Flask, render_template, request, redirect, session, flash
from db import get_connection
import pandas as pd

app = Flask(__name__)
app.secret_key = "mysecret123"


@app.route('/')
def home():
    return redirect('/login')

conn = get_connection()   # get connection
cursor = conn.cursor()    # create cursor
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

    import pandas as pd


    df = pd.read_sql("SELECT * FROM expense", conn)

    total_expense = df['amount'].sum()

    category_summary = df.groupby('category')['amount'].sum()

    # Create pie chart


    return render_template(
        'dashboard.html',
        total_expense=total_expense,
        category_summary=category_summary.to_dict()
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
@app.route("/add_expense", methods=["POST"])
def add_expense():

    user_id = request.form["us" \
    "er_id"]
    amount = request.form["Amount"]
    category = request.form["category"]
    date = request.form["date"]
    description = request.form["description"]

    query = """
    INSERT INTO expense (user_id, amount, category, date, description)
    VALUES (%s,%s,%s,%s,%s)
    """

    cursor.execute(query,(user_id,amount,category,date,description))
    db.commit()

    return "Expense Added Successfully"


# ADD INCOME
@app.route("/add_income", methods=["POST"])
def add_income():

    user_id = request.form["user_id"]
    amount = request.form["amount"]
    source = request.form["source"]
    date = request.form["date"]

    query = """
    INSERT INTO income (user_id, Amount, source, date)
    VALUES (%s,%s,%s,%s)
    """

    cursor.execute(query,(user_id,amount,source,date))
    db.commit()

    return "Income Added Successfully"


# ANALYTICS
@app.route("/analytics")
def analytics():

    df = pd.read_sql("SELECT * FROM expense", db)

    total_expense = df["amount"].sum()

    return f"Total Expense: {total_expense}"


# RUN SERVER (ALWAYS LAST)
if __name__ == "__main__":
    app.run(debug=True)