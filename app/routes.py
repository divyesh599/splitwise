# app/routes.py
from flask import jsonify, request
from app import app, db, mail, scheduler
from app.models import User, Expense, ExpensePaidBy, ExpenseOwedBy
from app.services import split_expense, send_weekly_balances




# API Routes
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    user_list = [{'userId': user.userId, 'name': user.name, 'email': user.email, 'mobileNumber': user.mobileNumber}
                 for user in users]
    return jsonify({'users': user_list})


@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.json  # Assuming you are sending JSON data in the request body

    name = data.get('name')
    email = data.get('email')
    mobile_number = data.get('mobileNumber')

    if not all([name, email, mobile_number]):
        return jsonify({'error': 'Missing required fields'}), 400

    new_user = User(name=name, email=email, mobileNumber=mobile_number)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User added successfully'}), 201



@app.route('/expenses', methods=['GET'])
def get_expenses():
    expenses = Expense.query.all()
    expense_list = [{'expenseId': expense.expenseId, 'type': expense.type, 'amount': float(expense.amount),
                     'simplifyFlag': expense.simplifyFlag, 'createdAt': expense.createdAt} for expense in expenses]
    return jsonify({'expenses': expense_list})



@app.route('/add_expense', methods=['POST'])
def add_expense():
    data = request.json
    print(data)
    # new_expense = Expense(type=data['type'], amount=data['amount'], simplifyFlag=data['simplifyFlag'])
    # db.session.add(new_expense)
    # db.session.commit()
    # participants = data.get('participants', [])
    # split_expense(new_expense, participants)
    # # Schedule weekly email notifications
    # scheduler.add_job(send_weekly_balances, 'interval', weeks=1)
    return jsonify({'message': 'Expense added successfully'})



