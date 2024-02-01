# app/routes.py
from flask import jsonify, request
from app import app, db, mail, scheduler
from app.models import User, Expense, ExpensePaidBy, ExpenseOwedBy
from app.services import (
    add_expense_paid_by,
    split_equally,
    split_expense,
    send_weekly_balances,
    delete_expense_owed_by,
    delete_expense,
    delete_expense_paid_by,
    is_expense_correct,
)


# API Routes
@app.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    user_list = [
        {
            "userId": user.userId,
            "name": user.name,
            "email": user.email,
            "mobileNumber": user.mobileNumber,
        }
        for user in users
    ]
    return jsonify({"users": user_list})


@app.route("/add_user", methods=["POST"])
def add_user():
    data = request.json  # Assuming you are sending JSON data in the request body

    name = data.get("name")
    email = data.get("email")
    mobile_number = data.get("mobileNumber")

    if not all([name, email, mobile_number]):
        return jsonify({"error": "Missing required fields"}), 400

    new_user = User(name=name, email=email, mobileNumber=mobile_number)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User added successfully"}), 201


@app.route("/expenses", methods=["GET"])
def get_expenses():
    expenses = Expense.query.all()
    expense_list = [
        {
            "expenseId": expense.expenseId,
            "type": expense.type,
            "amount": float(expense.amount),
            "simplifyFlag": expense.simplifyFlag,
            "createdAt": expense.createdAt,
        }
        for expense in expenses
    ]
    return jsonify({"expenses": expense_list})


@app.route("/add_expense", methods=["POST"])
def add_expense():
    data = request.json
    user_ids = {user.userId for user in User.query.all()}

    if not is_expense_correct(data):
        return jsonify({"error": "Amount mismatching"})

    if data["expense_type"] == "EQUAL":
        UID = 1
        expense = Expense(
            desc=data["desc"],
            amount=data["amount"],
            createdById=UID,
        )
        db.session.add(expense)
        db.session.commit()

        add_expense_paid_by(expense.expenseId, data["paidBy"])
        split_equally(expense.expenseId, user_ids, data["amount"])

    # # Schedule weekly email notifications
    # scheduler.add_job(send_weekly_balances, 'interval', weeks=1)
    return jsonify({"message": "Expense added successfully"})


@app.route("/delete", methods=["POST"])
def delete():
    temp = request.json["ID"]
    delete_expense(temp)
    delete_expense_owed_by(temp)
    delete_expense_paid_by(temp)
    return jsonify({"message": "Deleted.."})


@app.route("/delete_user", methods=["POST"])
def delete_user():
    temp = request.json["ID"]
    db.session.query(User).filter(User.userId == temp).delete()
    db.session.commit()
    return jsonify({"message": "Deleted.."})
