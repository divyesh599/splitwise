Here are the detailed SQL table definitions for the **Splitwise-like expense management system** that includes user authentication, group-based expenses, handling unregistered users, and tracking expenses.

### 1. **User Table** (For Registered Users)
This table stores all registered users' details, including authentication information.

```sql
CREATE TABLE User (
    userId INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    mobileNumber VARCHAR(15) NOT NULL UNIQUE,
    passwordHash VARCHAR(255) NOT NULL, -- Hashed password for security
    authToken VARCHAR(255), -- Token for authentication (JWT or similar)
    isActive BOOLEAN DEFAULT TRUE, -- Indicates if the user is active
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updatedAt TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### 2. **TemporaryUser Table** (For Unregistered Users)
This table stores details of users who are involved in expenses but are not yet registered.

```sql
CREATE TABLE TemporaryUser (
    tempUserId INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100), -- Nullable email, since it may not always be available
    mobileNumber VARCHAR(15),
    addedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3. **Group Table** (For Managing Groups)
This table stores group information for expenses that are managed in groups.

```sql
CREATE TABLE GroupTable (
    groupId INT PRIMARY KEY AUTO_INCREMENT,
    groupName VARCHAR(255) NOT NULL,
    createdById INT, -- The userId of the group creator
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updatedAt TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (createdById) REFERENCES User(userId) ON DELETE CASCADE
);
```

### 4. **GroupMember Table** (To Track Group Members)
This table stores the members of each group, including both registered and temporary users.

```sql
CREATE TABLE GroupMember (
    groupId INT,
    userId INT, -- Nullable, if the member is a registered user
    tempUserId INT, -- Nullable, if the member is a temporary user
    PRIMARY KEY (groupId, userId, tempUserId),
    FOREIGN KEY (groupId) REFERENCES GroupTable(groupId) ON DELETE CASCADE,
    FOREIGN KEY (userId) REFERENCES User(userId) ON DELETE CASCADE,
    FOREIGN KEY (tempUserId) REFERENCES TemporaryUser(tempUserId) ON DELETE CASCADE
);
```

### 5. **Expense Table** (To Manage Expenses)
This table stores the details of each expense, whether it's for a group or between users.

```sql
CREATE TABLE Expense (
    expenseId INT PRIMARY KEY AUTO_INCREMENT,
    description VARCHAR(255) NOT NULL,
    totalAmount DECIMAL(10, 2) NOT NULL,
    createdById INT, -- The userId of the expense creator
    groupId INT, -- Nullable if the expense is not tied to a group
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updatedAt TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (createdById) REFERENCES User(userId) ON DELETE CASCADE,
    FOREIGN KEY (groupId) REFERENCES GroupTable(groupId) ON DELETE CASCADE
);
```

### 6. **ExpensePaidBy Table** (To Track Who Paid How Much)
This table tracks how much each registered or temporary user paid towards an expense.

```sql
CREATE TABLE ExpensePaidBy (
    expenseId INT,
    userId INT, -- Nullable if the payer is a registered user
    tempUserId INT, -- Nullable if the payer is a temporary user
    amountPaid DECIMAL(10, 2) NOT NULL,
    PRIMARY KEY (expenseId, userId, tempUserId),
    FOREIGN KEY (expenseId) REFERENCES Expense(expenseId) ON DELETE CASCADE,
    FOREIGN KEY (userId) REFERENCES User(userId) ON DELETE CASCADE,
    FOREIGN KEY (tempUserId) REFERENCES TemporaryUser(tempUserId) ON DELETE CASCADE
);
```

### 7. **ExpenseOwedBy Table** (To Track Who Owes How Much)
This table tracks how much each registered or temporary user owes for an expense.

```sql
CREATE TABLE ExpenseOwedBy (
    expenseId INT,
    userId INT, -- Nullable if the debtor is a registered user
    tempUserId INT, -- Nullable if the debtor is a temporary user
    amountOwed DECIMAL(10, 2) NOT NULL,
    PRIMARY KEY (expenseId, userId, tempUserId),
    FOREIGN KEY (expenseId) REFERENCES Expense(expenseId) ON DELETE CASCADE,
    FOREIGN KEY (userId) REFERENCES User(userId) ON DELETE CASCADE,
    FOREIGN KEY (tempUserId) REFERENCES TemporaryUser(tempUserId) ON DELETE CASCADE
);
```

### 8. **Authentication Token Table (Optional)**
This table stores active authentication tokens for users. It is optional if you are using JWT or another token-based approach.

```sql
CREATE TABLE AuthToken (
    tokenId INT PRIMARY KEY AUTO_INCREMENT,
    userId INT,
    token VARCHAR(255) NOT NULL,
    expiresAt TIMESTAMP NOT NULL,
    FOREIGN KEY (userId) REFERENCES User(userId) ON DELETE CASCADE
);
```

### Key Workflow Scenarios

#### 1. **Creating an Expense Without a Group**
- The `groupId` in the `Expense` table can be `NULL`, which indicates an expense between individual users rather than a group.
  
#### 2. **Handling Unregistered Users**
- When creating an expense, if a participant is unregistered, add them to the `TemporaryUser` table.
- Use the `tempUserId` in the `ExpensePaidBy` and `ExpenseOwedBy` tables to track their involvement.
- Once they register, their data can be moved from the `TemporaryUser` to the `User` table.

#### 3. **User Authentication**
- Passwords are hashed before storage in the `User` table.
- Tokens are generated on login and stored in the `AuthToken` table (or handled using JWT in the backend).
- Routes that require authentication check the token validity.

### Summary of Database Structure

- **User Management**: `User` for registered users and `TemporaryUser` for unregistered users.
- **Expense Management**: `Expense`, `ExpensePaidBy`, and `ExpenseOwedBy` track the expenses and contributions.
- **Group Management**: `GroupTable` and `GroupMember` handle expenses within a group.
- **Authentication**: `AuthToken` (optional) or JWT for managing user sessions and protecting routes.

This structure should be flexible enough to handle group and individual expenses while allowing the system to involve both registered and unregistered users.
