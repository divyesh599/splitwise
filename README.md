# Splitwise - Expense Tracker System

The spiltwise is a simple application designed to help users track their expenses and manage shared expenses among a group of users.

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
- **createdById**: User ID of the creator of the expense.
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



## Installation

To use the Expense Tracker System, follow these steps:

1. Clone the repository: `git clone https://github.com/your/repo.git`
2. Install dependencies: `pip install`
3. Configure the database connection in `config.js`.
4. Run the application: `npm start`

## Contributing

If you would like to contribute to the project, please follow the [contribution guidelines](CONTRIBUTING.md).

## License

This Expense Tracker System is licensed under the [MIT License](LICENSE).
