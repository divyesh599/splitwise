I'm hoping the assignment will be reviewed on February 2, 2024, as I'm still making adjustments. Please note that I've had a busy schedule with full office work over the last two days.

# Expense Tracker System

The Expense Tracker System is a simple application designed to help users track their expenses and manage shared expenses among a group of users.

## Entity Descriptions

### User

- **userId**: Unique identifier for each user.
- **name**: Name of the user.
- **email**: Email address of the user.
- **mobileNumber**: Mobile number of the user.

### Expense

- **expenseId**: Unique identifier for each expense.
- **type**: Type or category of the expense.
- **amount**: Total amount of the expense.
- **participants**: List of users involved in the expense.
- **simplifyFlag**: Flag indicating whether the expense needs to be simplified.
- **createdAt**: Timestamp indicating when the expense was created.

### UserExpensePaid

- **user**: User who paid for the expense.
- **expense**: Expense for which the user made a payment.
- **amountPaid**: Amount paid by the user for the expense.

### UserExpenseOwed

- **user**: User who owes money for the expense.
- **expense**: Expense for which the user owes money.
- **amountOwed**: Amount owed by the user for the expense.

## Relationships

- The `User` entity is associated with the `UserExpensePaid` and `UserExpenseOwed` entities.
- The `Expense` entity is associated with the `UserExpensePaid` and `UserExpenseOwed` entities.

## Usage

1. **User Management**: Create, update, and delete user profiles.
2. **Expense Tracking**: Record and manage expenses with details like type, amount, and participants.
3. **Payment Tracking**: Track payments made by users for specific expenses.
4. **Owed Amounts**: Monitor amounts owed by users for shared expenses.

## Installation

To use the Expense Tracker System, follow these steps:

1. Clone the repository: `git clone https://github.com/your/repo.git`
2. Install dependencies: `npm install`
3. Configure the database connection in `config.js`.
4. Run the application: `npm start`

## Contributing

If you would like to contribute to the project, please follow the [contribution guidelines](CONTRIBUTING.md).

## License

This Expense Tracker System is licensed under the [MIT License](LICENSE).
