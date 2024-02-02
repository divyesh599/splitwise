# app/services.py
from app import db, mail, app, scheduler
from app.models import User, Expense, ExpensePaidBy, ExpenseOwedBy
from flask_mail import Message
from threading import Thread



def add_expense_paid_by(expense_id, paidBy):
    expense_paid_by_list = []

    for user_id, amount in paidBy.items():
        expense_paid_by_list.append(ExpensePaidBy(
            userId=int(user_id),
            expenseId=expense_id,
            amount=amount,
        ))

    db.session.add_all(expense_paid_by_list)
    db.session.commit()


def split_equally(expense_id, user_ids, total_amount):
    temp_amount = round(total_amount / len(user_ids), 2)

    expense_owed_by_list = []
    for user_id in user_ids:
        expense_owed_by_list.append(ExpenseOwedBy(
            userId=user_id,
            expenseId=expense_id,
            amount=temp_amount,
        ))
        total_amount -= temp_amount

    if total_amount != 0:
        expense_owed_by_list[0].amount += total_amount

    db.session.add_all(expense_owed_by_list)
    db.session.commit()

    return {"message" : "Expense split equally added successfully"}



def split_exactly(expense_id, owedBy):
    expense_owed_by_list = []

    for user_id, amount in owedBy.items():
        expense_owed_by_list.append(ExpenseOwedBy(
            userId=user_id,
            expenseId=expense_id,
            amount=amount,
        ))

    db.session.add_all(expense_owed_by_list)
    db.session.commit()

    return {"message" : "Expense split exactly added successfully"}




def split_percently(expense_id, owedBy, total_amount):
    expense_owed_by_list = []

    AMOUNT = total_amount
    for user_id, percent in owedBy.items():
        amount = round((percent / 100) * AMOUNT, 2)
        expense_owed_by_list.append(ExpenseOwedBy(
            userId=user_id,
            expenseId=expense_id,
            amount=amount,
        ))
        total_amount -= amount

    if total_amount != 0:
        expense_owed_by_list[0].amount += total_amount

    db.session.add_all(expense_owed_by_list)
    db.session.commit()

    return {"message" : "Expense split by percentage added successfully"}








def is_expense_correct(data):
    total_paid_amount = sum(data['paidBy'].values())
    if data['total_amount'] != total_paid_amount:
        return False
    
    return True




















# Function to split the expense among participants
def split_expense(expense, participants):
    total_amount = float(expense.amount)
    num_participants = len(participants)
    if num_participants == 0:
        return
    amount_per_person = round(total_amount / num_participants, 2)

    for user_id in participants:
        user_expense = UserExpense(
            userId=user_id, expenseId=expense.expenseId, amountOwed=amount_per_person
        )
        db.session.add(user_expense)

    db.session.commit()
    send_email_notifications(expense, participants)


# Asynchronous Email Notification Function
def send_email_notifications(expense, participants):
    with app.app_context():
        for user_id in participants:
            user = User.query.get(user_id)
            msg = Message(
                subject="New Expense Notification",
                sender="your_email@gmail.com",
                recipients=[user.email],
            )
            msg.body = f"You have been added to a new expense with ID: {expense.expenseId}. \
                         Total amount: {float(expense.amount):.2f} INR. \
                         You owe: {get_user_balance(user_id)} INR for this expense."
            Thread(target=mail.send, args=(msg,)).start()


# Function to calculate user balance for a given expense
def get_user_balance(user_id):
    user_expenses = UserExpense.query.filter_by(userId=user_id).all()
    total_owed = sum([float(expense.amountOwed) for expense in user_expenses])
    return round(total_owed, 2)


# Function to simplify expenses
def simplify_expenses():
    expenses = Expense.query.filter_by(simplifyFlag=True).all()
    for expense in expenses:
        participants = [user.userId for user in User.query.all()]
        split_expense(expense, participants)


# Function to send weekly email balances to users
def send_weekly_balances():
    with app.app_context():
        users = User.query.all()
        for user in users:
            msg = Message(
                subject="Weekly Balances Notification",
                sender="your_email@gmail.com",
                recipients=[user.email],
            )
            msg.body = f"Your total balance with all users: {get_user_total_balance(user.userId)} INR."
            Thread(target=mail.send, args=(msg,)).start()


# Function to calculate total balance for a user with all users
def get_user_total_balance(user_id):
    user_expenses = UserExpense.query.filter_by(userId=user_id).all()
    total_owed = sum([float(expense.amountOwed) for expense in user_expenses])
    return round(total_owed, 2)
