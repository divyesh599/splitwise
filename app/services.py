# app/services.py
from app import db, mail, app, scheduler
from app.models import User, Expense, ExpensePaidBy, ExpenseOwedBy
from flask_mail import Message
from threading import Thread


# Function to split the expense among participants
def split_expense(expense, participants):
    total_amount = float(expense.amount)
    num_participants = len(participants)
    if num_participants == 0:
        return
    amount_per_person = round(total_amount / num_participants, 2)
    
    for user_id in participants:
        user_expense = UserExpense(userId=user_id, expenseId=expense.expenseId, amountOwed=amount_per_person)
        db.session.add(user_expense)

    db.session.commit()
    send_email_notifications(expense, participants)

# Asynchronous Email Notification Function
def send_email_notifications(expense, participants):
    with app.app_context():
        for user_id in participants:
            user = User.query.get(user_id)
            msg = Message(subject='New Expense Notification',
                          sender='your_email@gmail.com',
                          recipients=[user.email])
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
            msg = Message(subject='Weekly Balances Notification',
                          sender='your_email@gmail.com',
                          recipients=[user.email])
            msg.body = f"Your total balance with all users: {get_user_total_balance(user.userId)} INR."
            Thread(target=mail.send, args=(msg,)).start()

# Function to calculate total balance for a user with all users
def get_user_total_balance(user_id):
    user_expenses = UserExpense.query.filter_by(userId=user_id).all()
    total_owed = sum([float(expense.amountOwed) for expense in user_expenses])
    return round(total_owed, 2)
