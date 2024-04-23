# app/models.py
from app import db


# Models
class User(db.Model):
    userId = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    mobileNumber = db.Column(db.String(20), nullable=False)


class Expense(db.Model):
    expenseId = db.Column(db.Integer, primary_key=True)
    desc = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.DECIMAL(15, 2), nullable=False)
    createdById = db.Column(db.Integer, nullable=False)
    createdAt = db.Column(
        db.TIMESTAMP,
        server_default=db.func.current_timestamp(),
        nullable=False
    )


class ExpensePaidBy(db.Model):
    userId = db.Column(
        db.Integer,
        db.ForeignKey("user.userId"),
        primary_key=True
    )
    expenseId = db.Column(
        db.Integer,
        db.ForeignKey("expense.expenseId"),
        primary_key=True
    )
    amount = db.Column(db.DECIMAL(15, 2), nullable=False)

    # Define the relationship with User and Expense
    user = db.relationship("User", backref="payments", lazy=True)
    expense = db.relationship("Expense", backref="payments", lazy=True)


class ExpenseOwedBy(db.Model):
    userId = db.Column(
        db.Integer,
        db.ForeignKey("user.userId"),
        primary_key=True
    )
    expenseId = db.Column(
        db.Integer,
        db.ForeignKey("expense.expenseId"),
        primary_key=True
    )
    amount = db.Column(db.DECIMAL(15, 2), nullable=False)

    # Define the relationship with User and Expense
    user = db.relationship("User", backref="expenses_owed", lazy=True)
    expense = db.relationship("Expense", backref="expenses_owed", lazy=True)
