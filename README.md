# Splitwise - Expense Tracker System

## Overview

Splitwise project is an example Flask web application designed to manage expenses among users. This README provides an overview of the project structure and how to run the application.

## Directory Structure

```lua
splitwise/
|-- app/
|   |-- __init__.py
|   |-- models.py
|   |-- routes.py
|   |-- services.py
|   |-- templates/
|   |-- static/
|-- config.py
|-- splitwise.db
|-- run.py
```



## Project Structure

- The `app/` directory is the core of the application, organized into the following components:

    - **`__init__.py`**: Initializes the Flask application.

    - **`models.py`**: Defines the database models.

    - **`routes.py`**: Manages route definitions and request handling logic.

    - **`services.py`**: Contains additional business logic or services.

    - **`templates/`**: This directory is a placeholder for HTML templates.

    - **`static/`**: Holds static files such as stylesheets and JavaScript.

- The `config.py` file serves as the configuration hub for the application.

- The `splitwise.db` file is an SQLite database used to store application data.

- The `run.py` script is designed to execute the Flask application.

## Getting Started

To run the application:

1. Install dependencies:

    ```bash
    pip install Flask Flask-SQLAlchemy Flask-Mail APScheduler Flask-Migrate
    ```

2. Navigate `splitwise/` directory.

    **Note:** Always remember to set up a virtual environment before installing dependencies to keep your project isolated.
    
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Run the application:

    ```bash
    python run.py
    ```

4. Access the application at [http://localhost:5000/](http://localhost:5000/).








## Class Diagram

### User

- **userId**
- name
- email
- mobileNumber

### Expense

- **expenseId**
- desc
- amount
- createdById
- createdAt

### ExpensePaidBy

- **userId**
- **expenseId**
- amount

### ExpenseOwedBy

- **userId**
- **expenseId**
- amount

## Database Model

### User

- **userId**: Integer (Primary Key)
- **name**: String (255), Not Null
- **email**: String (255), Unique, Not Null
- **mobileNumber**: String (20), Not Null

### Expense

- **expenseId**: Integer (Primary Key)
- **desc**: String (255), Not Null
- **amount**: Decimal (15, 2), Not Null
- **createdById**: Integer, Not Null
- **createdAt**: Timestamp, Default: Current Timestamp

### ExpensePaidBy

- **userId**: Integer (Foreign Key to User.userId, Primary Key)
- **expenseId**: Integer (Foreign Key to Expense.expenseId, Primary Key)
- **amount**: Decimal (15, 2), Not Null

### ExpenseOwedBy

- **userId**: Integer (Foreign Key to User.userId, Primary Key)
- **expenseId**: Integer (Foreign Key to Expense.expenseId, Primary Key)
- **amount**: Decimal (15, 2), Not Null


## Entity Descriptions

### User

- **userId**: Unique identifier for each user.
- **name**: Name of the user.
- **email**: Email address of the user.
- **mobileNumber**: Mobile number of the user.

### Expense

- **expenseId**: Unique identifier for each expense.
- **desc**: Description of the expense.
- **amount**: Total amount of the expense.
- **createdById**: User ID of the creator of the expense. Default: userId = 1
- **createdAt**: Timestamp indicating when the expense was created.

### ExpensePaidBy

- **user**: User who paid for the expense.
- **expense**: Expense for which the user made a payment.
- **amountPaid**: Amount paid by the user for the expense.

### ExpenseOwedBy

- **user**: User who owes money for the expense.
- **expense**: Expense for which the user owes money.
- **amountOwed**: Amount owed by the user for the expense.

## Relationships

- The `User` entity is associated with the `UserExpensePaid` and `UserExpenseOwed` entities.
- The `Expense` entity is associated with the `UserExpensePaid` and `UserExpenseOwed` entities.


# Splitwise API Documentation

### 1. Get Users

- **Endpoint:** `/users`  
- **Method:** GET  
- **Description:** Retrieves a list of all users.  
- **Response Format:**
    ```json
    {
    "users": [
        {
        "userId": 1,
        "name": "John Doe",
        "email": "john.doe@example.com",
        "mobileNumber": "123-456-7890"
        },
        // Additional user objects...
    ]
    }
    ```

### 2. Add User

- **Endpoint:** `/add_user`  
- **Method:** POST  
- **Description:** Adds a new user to the system.  
- **Request Format:**
    ```json
    {
    "name": "John Doe",
    "email": "john.doe@example.com",
    "mobileNumber": "123-456-7890"
    }
    ```
- **Response Format:**
    ```json
    {
    "message": "User added successfully"
    }
    ```

### 3. Add Expense

**Equal Split**
- **Endpoint:** `/add_expense`
- **Method:** POST
- **Description:** Adds a new expense along with expense-related details.
- **Request Format:**
    ```json
    {
    "expense_type": "EQUAL",
    "desc": "electricity bill",
    "total_amount": 500,
    "paidBy": {
        "2": 200,
        "3": 300
    }
    }
    ```
- **Response Format:**
    ```json
    {
    "message": "Expense split equally added successfully"  // or details of any errors
    }
    ```

**Exact Split**
- **Endpoint:** `/add_expense`
- **Method:** POST
- **Description:** Adds a new expense along with expense-related details.
- **Request Format:**
    ```json
    {
    "expense_type": "EXACT",
    "desc": "paytm",
    "total_amount": 600,
    "paidBy": {
        "1": 300,
        "3": 300
    },
    "owedBy": {
        "1": 100,
        "3": 200,
        "4": 300
    }
    }
    ```
- **Response Format:**
    ```json
    {
    "message": "Expense split exactly added successfully"  // or details of any errors
    }
    ```

**Percent Split**
- **Endpoint:** `/add_expense`
- **Method:** POST
- **Description:** Adds a new expense along with expense-related details.
- **Request Format:**
    ```json
    {
    "expense_type": "PERCENT",
    "desc": "paytm",
    "total_amount": 700,
    "paidBy": {
        "1": 700
    },
    "owedBy": {
        "1": 20,
        "2": 33,
        "3": 47
    }
    }
    ```

- **Response Format:**
    ```json
    {
    "message": "Expense split by percentage added successfully"  // or details of any errors
    }
    ```









