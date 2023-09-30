from cs50 import SQL
from flask import Flask, flash, redirect, render_template, url_for, request, session, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required, usd, apology, time, none_look, get_next_due_date, pct

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd
app.jinja_env.filters["time"] = time
app.jinja_env.filters["none_look"] = none_look
app.jinja_env.filters["due_date"] = get_next_due_date
app.jinja_env.filters["pct"] = pct

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///financial_life.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/testing", methods=["GET", "POST"])
@login_required
def testing():
    """Page for testing"""
    if request.method == "POST":
        data = request.json

        try:
            # assign updated data to variables
            row_id = data["id"]
            new_name = data["name"]
            new_age = data["age"]

            # Update the database
            db.execute(
                "UPDATE testing SET name = ?, age = ? WHERE id = ?",
                new_name,
                new_age,
                row_id,
            )

            # Optionally use flash messages for user feedback
            flash("Table data updated.", "info")

            print("Update successful")

            # Redirect to the desired route after the update
            return jsonify(needsRedirect=True, redirectUrl=url_for("testing"))

        except Exception as e:
            print(f"Error updating row: {e}")

    else:
        rows = db.execute("SELECT * FROM testing")
        return render_template("testing.html", rows=rows)


@app.route("/testing_delete", methods=["POST"])
@login_required
def testing_delete():
    """Page for testing: delete rows"""
    data = request.json

    try:
        # Update the database
        db.execute(
            "DELETE FROM testing WHERE id = ?",
            data["id"],
        )

        # Optionally use flash messages for user feedback
        flash("Table entry deleted.", "info")

        print("Table row deletion successful")

        # Redirect to the desired route after the update
        return jsonify(needsRedirect=True, redirectUrl=url_for("testing"))

    except Exception as e:
        print(f"Error updating row: {e}")


@app.route("/testing_add", methods=["POST"])
@login_required
def testing_add():
    """Page for testing: add rows"""

    try:

        if not (name := request.form.get("name")):
            return apology("You must provide a name")
        if not (age := request.form.get("age")):
            return apology("You must provide an age")

        # add person into table
        db.execute(
            "INSERT INTO testing (name, age) VALUES(?, ?)",
            name,
            age,
        )

        flash("Person added.", "info")
        print("TESTING: Person added")

        return redirect(url_for("testing"))

    except Exception as e:
        print(f"Error updating row: {e}")


@app.route("/transactions")
@login_required
def transactions():
    """Show history of transactions"""
    # SQL query to return accounts
    transactions = db.execute("SELECT * FROM transactions WHERE user_id = ? AND ((category <> 'IOU' AND category <> 'IOU Payment') OR category IS NULL)", session["user_id"])

    return render_template("transactions.html", transactions=transactions)


@app.route("/add_transfer", methods=["POST"])
@login_required
def add_transfer():
    """Record a money transfer (account to account, like paying off a CC)"""
    # get necessary lists for back-end validation
    payment_methods = db.execute("SELECT name FROM accounts WHERE user_id = ?", session["user_id"])
    pm_list = []
    for account in payment_methods:
        pm_list.append(account["name"])

    # gather all form data
    if not (date := request.form.get("date")):
        return apology("You must provide a transaction date")
    if not (time := request.form.get("time")):
        time = None
    if not (amount := request.form.get("amount")):
        return apology("You must provide a transaction amount")
    else:
        amount = amount.replace("$", "")
    notes = request.form.get("notes")
    category = "Transfer"

    # extra validation on back-end
    if not (source_account := request.form.get("source_account")) in pm_list:
        return apology("You must select an appropriate source account")
    if not (target_account := request.form.get("target_account")) in pm_list:
        return apology("You must select an appropriate target account")

    item = f"TRANSFER: {source_account} to {target_account}"

    # enter transaction into table
    db.execute(
        "INSERT INTO transactions (user_id, amount, target_account, payment_method, notes, date, time, category, item) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)",
        session["user_id"],
        amount,
        target_account,
        source_account,
        notes,
        date,
        time,
        category,
        item,
    )

    # update account balances
    db.execute(
        "UPDATE accounts SET balance = (balance - ?) WHERE user_id = ? AND name = ?",
        amount,
        session["user_id"],
        source_account,
    )

    db.execute(
        "UPDATE accounts SET balance = (balance + ?) WHERE user_id = ? AND name = ?",
        amount,
        session["user_id"],
        target_account,
    )

    print("Transfer recorded.")
    flash("Transfer recorded.", "info")

    return redirect(url_for("transactions"))


@app.route("/pay_cc", methods=["POST"])
@login_required
def pay_cc():
    """Record a credit card payment"""
    # get necessary lists for back-end validation
    payment_methods = db.execute("SELECT name FROM accounts WHERE user_id = ?", session["user_id"])
    pm_list = []
    for account in payment_methods:
        pm_list.append(account["name"])

    # gather all form data
    if not (date := request.form.get("date")):
        return apology("You must provide a transaction date")
    time = request.form.get("time")
    if not (amount := request.form.get("amount")):
        return apology("You must provide an amount")
    else:
        amount = amount.replace("$", "")
        try:
            if float(amount) <= 0:
                return apology("You must provide a positive amount")
        except ValueError:
            return apology("You must only provide numbers and a decimal point, if needed")

    notes = request.form.get("notes")
    category = "Credit Card Payment"

    # extra validation on back-end
    if not (source_account := request.form.get("source_account")) in pm_list:
        return apology("You must select an appropriate source account")
    if not (target_account := request.form.get("target_account")) in pm_list:
        return apology("You must select an appropriate target account")

    item = f"PAYMENT: {target_account}"

    # enter transaction into table
    db.execute(
        "INSERT INTO transactions (user_id, amount, target_account, payment_method, notes, date, time, category, item) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)",
        session["user_id"],
        amount,
        target_account,
        source_account,
        notes,
        date,
        time,
        category,
        item,
    )

    # update account balances
    db.execute(
        "UPDATE accounts SET balance = (balance - ?) WHERE user_id = ? AND name = ?",
        amount,
        session["user_id"],
        source_account,
    )

    db.execute(
        "UPDATE accounts SET balance = (balance - ?) WHERE user_id = ? AND name = ?",
        amount,
        session["user_id"],
        target_account,
    )

    print("CC payment recorded.")
    flash("Credit card payment recorded.", "info")

    return redirect(url_for("transactions"))


@app.route("/iou")
@login_required
def iou():
    """Show record of IOUs"""
    # SQL query to return IOU accounts
    iou_transactions = db.execute("SELECT * FROM transactions WHERE user_id = ? AND ((category = 'IOU' AND amount > 0) OR (category = 'IOU Payment' AND amount < 0))",
                                  session["user_id"],
                                  )
    iou_payment_transactions = db.execute("SELECT * FROM transactions WHERE user_id = ? AND ((category = 'IOU' AND amount < 0) OR (category = 'IOU Payment' AND amount > 0))",
                                  session["user_id"],
                                  )
    # check for no IOU transactions
    if not iou_transactions and not iou_payment_transactions:
        flash("No IOUs have been created yet.", "info")
        return redirect(url_for("add_transaction"))

    # SQL query: return names, cumulative amounts per person
    cumulative_owed = db.execute("SELECT target_account as person, SUM(amount) as total FROM transactions WHERE user_id = ? AND (category = 'IOU' OR category = 'IOU Payment') GROUP BY target_account HAVING SUM(amount) > 0",
                                  session["user_id"],
                                  )
    cumulative_owed_to_you = db.execute("SELECT target_account as person, SUM(amount) as total FROM transactions WHERE user_id = ? AND (category = 'IOU' OR category = 'IOU Payment') GROUP BY target_account HAVING SUM(amount) < 0",
                                  session["user_id"],
                                  )

    return render_template("iou.html", iou_trans=iou_transactions, iou_pay=iou_payment_transactions, cum_owed=cumulative_owed, cum_owed_to_you=cumulative_owed_to_you)


@app.route("/pay_iou", methods=["POST"])
@login_required
def pay_iou():
    """Record a payment towards IOU"""
    # get necessary lists for back-end validation
    payment_methods = db.execute("SELECT name FROM accounts WHERE user_id = ?", session["user_id"])
    pm_list = []
    for account in payment_methods:
        pm_list.append(account["name"])

    # gather all form data
    if not (date := request.form.get("date")):
        return apology("You must provide a transaction date")
    time = request.form.get("time")
    if not (amount := request.form.get("amount")):
        return apology("You must provide an amount")
    else:
        amount = amount.replace("$", "")
        if float(amount) < 0:
            flash("Entry had a negative amount.", "warning")
    if not (person := request.form.get("company")):
        return apology("You must provide the name of the person you are creating the obligation toward.")
    direction = request.form.get("iou_direction")
    print(f"DIRECTION: {direction}")

    if direction == "to_others":
        amount = (float(amount) * -1)
    notes = request.form.get("notes")
    category = "IOU Payment"

    if not (source_account := request.form.get("source_account")) in pm_list:
        return apology("You must select an appropriate account")

    # enter transaction into transactions table
    db.execute(
        "INSERT INTO transactions (user_id, amount, target_account, category, notes, date, time, payment_method) VALUES(?, ?, ?, ?, ?, ?, ?, ?)",
        session["user_id"],
        amount,
        person,
        category,
        notes,
        date,
        time,
        source_account,
    )

    # adjust necessary account
    # currently verbose but might change overall structure later
    if direction == "to_you":
        db.execute(
                "UPDATE accounts SET balance = (balance + ?) WHERE user_id = ? AND name = ?",
                amount,
                session["user_id"],
                source_account,
            )
    else:
        db.execute(
                "UPDATE accounts SET balance = (balance + ?) WHERE user_id = ? AND name = ?",
                amount,
                session["user_id"],
                source_account,
            )

    print("IOU transaction recorded.")
    flash("IOU transaction recorded.", "info")

    return redirect(url_for("iou"))


@app.route("/create_iou", methods=["POST"])
@login_required
def create_iou():
    """Record an IOU creation"""
    # gather all form data
    if not (date := request.form.get("date")):
        return apology("You must provide a transaction date")
    time = request.form.get("time")
    if not (amount := request.form.get("amount")):
        return apology("You must provide an amount")
    else:
        amount = amount.replace("$", "")
        if float(amount) < 0:
            flash("Entry had a negative amount.", "warning")
    if not (person := request.form.get("company")):
        return apology("You must provide the name of the person you are creating the obligation toward.")
    direction = request.form.get("iou_direction")
    print(f"DIRECTION: {direction}")

    if direction == "to_you":
        amount = (float(amount) * -1)
    notes = request.form.get("notes")
    category = "IOU"

    # enter transaction into transactions table
    db.execute(
        "INSERT INTO transactions (user_id, amount, target_account, category, notes, date, time) VALUES(?, ?, ?, ?, ?, ?, ?)",
        session["user_id"],
        amount,
        person,
        category,
        notes,
        date,
        time,
    )

    print("IOU creation recorded.")
    flash("IOU creation recorded.", "info")

    return redirect(url_for("iou"))


@app.route("/add_transaction", methods=["GET", "POST"])
@login_required
def add_transaction():
    """Record a transaction"""
    if request.method == "POST":

        # get necessary lists for back-end validation
        payment_methods = db.execute("SELECT name FROM accounts WHERE user_id = ?", session["user_id"])
        pm_list = []
        for account in payment_methods:
            pm_list.append(account["name"])

        gc_payment_methods = db.execute("SELECT company FROM gift_cards WHERE user_id = ? AND current_balance > 0", session["user_id"])
        gc_pm_list = []
        for row in gc_payment_methods:
            gc_pm_list.append(row["company"])

        categories = db.execute("SELECT name FROM categories WHERE user_id = ?", session["user_id"])
        cat_list = []
        for cat in categories:
            cat_list.append(cat["name"])

        # gather all form data
        if not (date := request.form.get("date")):
            return apology("You must provide a transaction date")
        if not (time := request.form.get("time")):
            time = None
        if not (amount := request.form.get("amount")):
            return apology("You must provide a transaction amount")
        else:
            amount = amount.replace("$", "")
            if float(amount) < 0:
                flash("Entry had a negative amount.", "warning")
        if not (item := request.form.get("item")):
            return apology("You must provide the item the transaction relates to")
        if not (company := request.form.get("company")):
            return apology("You must provide the company related to the transaction")
        notes = request.form.get("notes")

        # extra validation on back-end
        if not (category := request.form.get("category")) in cat_list:
            return apology("You must select from the created categories")

        # check for gift card usage
        if not (gc_used := request.form.get("gc_used")):
            print(f"GC USED VALUE:\n\n{gc_used}\n\n")

            # extra validation on back-end
            if not (payment_method := request.form.get("payment_method")) in pm_list:
                return apology("You must select an appropriate payment method")

            # enter transaction into table
            db.execute(
                "INSERT INTO transactions (user_id, amount, item, target_account, payment_method, category, notes, date, time) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)",
                session["user_id"],
                amount,
                item,
                company,
                payment_method,
                category,
                notes,
                date,
                time,
            )

            # update account balance
            db.execute(
                "UPDATE accounts SET balance = (balance - ?) WHERE user_id = ? AND name = ?",
                amount,
                session["user_id"],
                payment_method,
            )

            # check for overdraft
            updated_accounts = db.execute("SELECT * FROM accounts WHERE user_id = ? AND name = ?", session["user_id"], payment_method)
            if updated_accounts[0]["type"] != "Credit Card" and updated_accounts[0]["balance"] < 0:
                print("This transaction appears to have overdrawn the specified account")
                flash("This transaction appears to have overdrawn the specified account.", "warning")
        else:
            gc_used = True
            print(f"GC USED VALUE:\n\n{gc_used}\n\n")

            # extra validation on back-end
            if not (gc_payment_method := request.form.get("gc_payment_method")) in gc_pm_list:
                return apology("You must select an existing gift card with a balance greater than 0")

            # verify GC selected matches company name
            if gc_payment_method != company:
                return apology("You must select a gift card that matches the company")

            # prevent over-charging a gift card
            current_balance = db.execute(
                "SELECT current_balance FROM gift_cards WHERE user_id = ? AND company = ?",
                session["user_id"],
                gc_payment_method,
            )[0]["current_balance"]

            if float(amount) > current_balance:
                return apology("You can't spend more than the current balance of the gift card")

            # enter transaction into table
            db.execute(
                "INSERT INTO transactions (user_id, amount, item, target_account, payment_method, category, notes, date, time) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)",
                session["user_id"],
                amount,
                item,
                company,
                f"Gift Card: {gc_payment_method}",
                category,
                notes,
                date,
                time,
            )

            # update gift card's current balance
            db.execute(
                "UPDATE gift_cards SET current_balance = (current_balance - ?) WHERE user_id = ? AND company = ?",
                amount,
                session["user_id"],
                company,
            )

        print("Transaction recorded.")
        flash("Transaction recorded.", "info")

        return redirect(url_for("transactions"))

    else:
        # SQL queries to return payment methods and spending categories; sorted ABC
        payment_methods = db.execute("SELECT name, credit_card FROM accounts WHERE user_id = ?", session["user_id"])
        payment_methods = sorted(payment_methods, key=lambda x: x['name'])

        gc_payment_methods = db.execute(
            "SELECT company FROM gift_cards WHERE user_id = ? AND current_balance > 0",
            session["user_id"]
            )
        gc_payment_methods = sorted(gc_payment_methods, key=lambda x: x['company'])


        categories = db.execute("SELECT name FROM categories WHERE user_id = ?", session["user_id"])
        cat_list = []
        for cat in categories:
            cat_list.append(cat["name"])
        spending_categories = sorted(cat_list)

        return render_template("add_transaction.html", payment_methods=payment_methods, gc_payment_methods=gc_payment_methods, categories=spending_categories)


@app.route("/accounts", methods=["GET", "POST"])
@login_required
def accounts():
    """Shows users accounts and allows adding more"""

    if request.method == "POST":
        # SQL query to add accounts
        """Add account"""
        if request.method == "POST":
            if not (name := request.form.get("name")):
                return apology("You must provide the account name")
            if not (a_type := request.form.get("type")):
                return apology("You must provide an account type")
            if a_type == "Credit Card":
                cc_status = 1
            else:
                cc_status = 0
            starting_balance = request.form.get("balance")
            if (percentage := request.form.get("percentage")) and float(percentage) < 0:
                return apology("You can't provide a negative interest rate")
            due_date = request.form.get("due_date")

            db.execute(
                "INSERT INTO accounts (user_id, name, type, balance, percentage, credit_card, due_date) VALUES(?, ?, ?, ?, ?, ?, ?)",
                session["user_id"],
                name,
                a_type,
                starting_balance,
                percentage,
                cc_status,
                due_date,
            )
            print("Account added.")
            flash("New account added!", "info")
            return redirect(url_for("accounts"))

        return render_template("accounts.html")

    else:
        # SQL query to return accounts
        accounts = db.execute("SELECT name, type, balance, credit_card, percentage, due_date FROM accounts WHERE user_id = ?", session["user_id"])
        account_types = db.execute("SELECT name FROM account_types WHERE user_id = ? OR user_id = ?", session["user_id"], 0)

        account_types = sorted(account_types, key=lambda x: x["name"])

        cc_accounts = []
        non_cc_accounts = []

        for account in accounts:
            if account["type"] == "Credit Card":
                cc_accounts.append(account)
            else:
                non_cc_accounts.append(account)

        cc_accounts = sorted(cc_accounts, key=lambda x: x["name"])
        non_cc_accounts = sorted(non_cc_accounts, key=lambda x: x["name"])

        due_date_options = [str(i) for i in range(1, 32)] + ["EOM"]

        return render_template("accounts.html", cc_accounts=cc_accounts, non_cc_accounts=non_cc_accounts, account_types=account_types, due_date_options=due_date_options)


@app.route("/")
@login_required
def index():
    """Show helpul basic info OR if new account, links to add basic items"""

    return redirect(url_for("accounts"))
    # return render_template("index.html")


@app.route("/gift_cards")
@login_required
def gift_cards():
    """Show gift cards with current balances (and maybe relevant transactions)"""
    gift_cards = db.execute("SELECT * FROM gift_cards WHERE user_id = ?", session["user_id"])

    gift_cards_list = []

    for card in gift_cards:
        if not float(card["current_balance"]) == 0:
            gift_cards_list.append(card)

    gift_cards_list = sorted(gift_cards_list, key=lambda x: x["company"])

    return render_template("gift_cards.html", gift_cards_list=gift_cards_list)


@app.route("/gift_cards_update", methods=["POST"])
@login_required
def gift_cards_update():
    """Update GC balances/names"""
    print("SOMETHING HAPPENS")
    data = request.json
    print(f"DATA:\n{data}\n\n\n")

    try:
        # assign updated data to variables
        row_id = data["id"]
        company = data["company"]
        current_balance = data["current_balance"].strip().replace("$", "").replace(",", "")
        starting_balance = data["starting_balance"].strip().replace("$", "").replace(",", "")

        # Update the database
        db.execute(
            "UPDATE gift_cards SET company = ?, current_balance = ?, starting_balance = ? WHERE id = ? AND user_id = ?",
            company,
            current_balance,
            starting_balance,
            row_id,
            session["user_id"],
        )
        # Feedback to user via flash message and print to console
        flash("Table data updated.", "info")
        print("Gift card data update successful")

        # Redirect to the desired route after the update
        return jsonify(needsRedirect=True, redirectUrl=url_for("gift_cards"))
    except Exception as e:
        print(f"Error updating row: {e}")


@app.route("/gift_cards_add", methods=["POST"])
@login_required
def gift_cards_add():
    """Add gift cards"""
    if request.method == "POST":
        if not (company := request.form.get("company")):
            return apology("You must provide the company that the gift card is for")
        if not (starting_balance := request.form.get("starting_balance")):
            return apology("You must provide a starting balance")
        if float(starting_balance) < 0:
            return apology("Your gift card can't have a negative balance")
        if not (current_balance := request.form.get("current_balance")):
            return apology("You must provide the current balance")
        if float(current_balance) > float(starting_balance):
            return apology("Your gift card's current balance can't be higher than the starting balance")

        # enter transaction into table
        db.execute(
            "INSERT INTO gift_cards (user_id, company, starting_balance, current_balance) VALUES(?, ?, ?, ?)",
            session["user_id"],
            company,
            starting_balance,
            current_balance,
        )

        flash("Gift card added.", "info")
        print("Gift card added")

        return redirect(url_for("gift_cards"))


@app.route("/gift_cards_delete", methods=["POST"])
@login_required
def gift_cards_delete():
    """Remove gift cards"""
    data = request.json

    try:
        # Update the database
        db.execute(
            "DELETE FROM gift_cards WHERE user_id = ? AND id = ?",
            session["user_id"],
            data["id"],
        )

        # Optionally use flash messages for user feedback
        flash("Gfit card deleted.", "info")

        print("Gift card deletion successful")

        # Redirect to the desired route after the update
        return jsonify(needsRedirect=True, redirectUrl=url_for("gift_cards"))

    except Exception as e:
        print(f"Error updating row: {e}")


@app.route("/savings")
@login_required
def savings():
    """Show savings breakdown"""
    accounts = db.execute("SELECT name, type, balance, percentage FROM accounts WHERE user_id = ?", session["user_id"])
    savings = db.execute("SELECT * FROM savings WHERE user_id = ?", session["user_id"])

    accounts_list = []
    savings_list = []

    for account in accounts:
        if account["type"] == "Savings Account":
            accounts_list.append(account)

    for item in savings:
        if account["type"] == "Savings Account":
            savings_list.append(item)

    accounts_list = sorted(accounts_list, key=lambda x: x["name"])
    savings_list = sorted(savings_list, key=lambda x: x["item"])

    return render_template("savings.html", accounts_list=accounts_list, savings_list=savings_list)


@app.route("/income")
@login_required
def income():
    """Show income sources"""

    return render_template("income.html")


@app.route("/add_income", methods=["POST"])
@login_required
def add_income():
    """Add transaction categories"""
    # if not (name := request.form.get("name")):
    #     return apology("You must provide a category name")
    # else:
    #     name = name.title()

    # db.execute(
    #     "INSERT INTO categories (user_id, name) VALUES(?, ?)",
    #     session["user_id"],
    #     name,
    # )
    #
    # print("Catgory added.")
    # flash("New category added!", "info")
    return redirect(url_for("manage_account"))


@app.route("/add_category", methods=["POST"])
@login_required
def add_category():
    """Add transaction categories"""
    if request.method == "POST":
        if not (name := request.form.get("name")):
            return apology("You must provide a category name")
        else:
            name = name.title()

        db.execute(
            "INSERT INTO categories (user_id, name) VALUES(?, ?)",
            session["user_id"],
            name,
        )
        print("Catgory added.")
        flash("New category added!", "info")
        return redirect(url_for("manage_account"))


@app.route("/add_account_type", methods=["POST"])
@login_required
def add_account_type():
    """Add account types"""
    if request.method == "POST":
        if not (name := request.form.get("name")):
            return apology("You must provide an account type name")
        else:
            name = name.title()

        db.execute(
            "INSERT INTO account_types (user_id, name) VALUES(?, ?)",
            session["user_id"],
            name,
        )
        print("Account type added.")
        flash("New account type added!", "info")
        return redirect(url_for("manage_account"))


@app.route("/manage_account", methods=["GET"])
@login_required
def manage_account():
    """Add transaction categories, change password, etc."""
    categories = db.execute("SELECT name FROM categories WHERE user_id = ?", session["user_id"])
    cat_list = []
    for cat in categories:
        cat_list.append(cat["name"])

    # get default account types (user_id = 0)
    account_types = db.execute("SELECT name FROM account_types WHERE user_id = ?", 0)
    account_types_list = []
    for type in account_types:
        account_types_list.append(type["name"])
    # get user specific account types
    account_types = db.execute("SELECT name FROM account_types WHERE user_id = ?", session["user_id"])
    for type in account_types:
        account_types_list.append(type["name"])

    return render_template("manage_account.html", categories=sorted(cat_list), types=sorted(account_types_list))


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect(url_for("index"))

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    flash("You have been logged out", "info")
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # If already logged in, clear session
    session.clear()

    # User reached route via POST
    if request.method == "POST":
        # Check if username already exists; if yes, tell user
        # If not; add user to DB

        user = request.form.get("username")
        password = request.form.get("password")
        pass_check = request.form.get("confirmation")

        # Ensure username was submitted
        if not user:
            # alert_msg = "must provide username"
            return apology("must provide username")

        # Ensure password was submitted
        elif not password:
            return apology("must provide password")

        # Ensure passwords matched
        elif not pass_check or pass_check != password:
            return apology("passwords must match")
        hashed_pass = generate_password_hash(
            password, method="pbkdf2:sha1", salt_length=8
        )

        # Query database for username
        if db.execute("SELECT * FROM users WHERE username = ?", user):
            return apology("username already exists")

        # Ensure username exists and password is correct

        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", user, hashed_pass)
        print("User registered")
        flash("New account created! You may now log in.", "info")
        return redirect(url_for("index"))

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")