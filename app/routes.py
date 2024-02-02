# app/routes.py
from flask import jsonify, request
from sqlalchemy.orm import aliased
from app import app, db, mail, scheduler
from app.models import User, Expense, ExpensePaidBy, ExpenseOwedBy
from app.services import (
    add_expense_paid_by,
    split_equally,
    split_exactly,
    split_percently,
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


@app.route("/add_expense", methods=["POST"])
def add_expense():
    data = request.json
    user_ids = {user.userId for user in User.query.all()}

    if not is_expense_correct(data):
        return jsonify({"error": "Given data mismatching."})

    # Assuming pre-validation, we proceed with the expectation of correct data.

    # Add Expense
    UID = 1  # Default creator ID for expenses
    expense = Expense(
        desc=data["desc"],
        amount=data["total_amount"],
        createdById=UID,
    )
    db.session.add(expense)
    db.session.commit()

    # Add Expense Paid By
    add_expense_paid_by(expense.expenseId, data["paidBy"])

    # Add Expense Owed By
    message = {}
    if data["expense_type"] == "EQUAL":
        message = split_equally(
            expense.expenseId, user_ids, data["total_amount"])
    elif data["expense_type"] == "EXACT":
        message = split_exactly(expense.expenseId, data["owedBy"])
    elif data["expense_type"] == "PERCENT":
        message = split_percently(
            expense.expenseId, data["owedBy"], data["total_amount"]
        )

    # # Schedule weekly email notifications
    # scheduler.add_job(send_weekly_balances, 'interval', weeks=1)
    return jsonify(message)


@app.route("/delete_expense", methods=["POST"])
def delete_expense():
    IDs = request.json["ID"]
    db.session.query(Expense).filter(Expense.expenseId.in_(IDs)).delete(
        synchronize_session=False
    )
    db.session.query(ExpenseOwedBy).filter(ExpenseOwedBy.expenseId.in_(IDs)).delete(
        synchronize_session=False
    )
    db.session.query(ExpensePaidBy).filter(ExpensePaidBy.expenseId.in_(IDs)).delete(
        synchronize_session=False
    )
    db.session.commit()
    return jsonify({"message": "Deleted.."})


@app.route("/delete_user", methods=["POST"])
def delete_user():
    IDs = request.json["ID"]
    db.session.query(User).filter(User.userId.in_(IDs)).delete(
        synchronize_session=False
    )
    db.session.commit()
    return jsonify({"message": "Deleted.."})


# @app.route("/expenses", methods=["GET"])
# def get_expenses():
#     expenses = Expense.query.all()
#     expense_list = [
#         {
#             "expenseId": expense.expenseId,
#             "type": expense.type,
#             "amount": float(expense.amount),
#             "simplifyFlag": expense.simplifyFlag,
#             "createdAt": expense.createdAt,
#         }
#         for expense in expenses
#     ]
#     return jsonify({"expenses": expense_list})
