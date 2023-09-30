# Money Bags | CS50x
#### Video Demo: https://youtu.be/6ze5NUPtkE4
#### Description:

## Purpose

This repository represents a Python project to fulfill the final project requirements for Harvard University's CS50x, Introduction to Computer Science.

All rights are reserved by the original project creator, Jasper Davis.

## Overview

This is a python-based web application that supports a wide array of financial information tracking, including:
- Creating various financial accounts (e.g. credit cards, savings accounts, cryptocurrency, etc.)
- Creating gift cards and using them as a payment method for recorded transactions
- Recording Transactions (of five different transaction types, including the recording and payment of IOUs)

The technical stack:
- Python (using Flask) on the backend
- SQLite as the backend database
- HTML, CSS, & JavaScript on the frontend

In the future, I'd like to migrate from SQLite to PostgreSQL. I will also be exploring how the project might be improved if moving from Flask to Django.

## Instructions

### Dependencies

This program makes use of the following libraries:
- cs50 | for simplified execution of SQL queries
- flask & flask_session | for handling dynamic generation of webpage content and managing user sessions
- werkzeug.security | for generating and checking password hashes for user accounts

### Inital Setup

The program can be executed from the command line using `flask run` in the main project directory:

Once the flask webserver is running, you'll be able to access the web application from a web browser (currently tested with Safari and Chrome on MacOS). Initially, you'll need to register for a user account by selecting a username and password.

Once your account is created, you can login.

#### Accounts

Once logged in, you are redirected to the `Accounts` page.
On this page, you'll see two tables.
- One showing all your bank accounts, digital wallets, cash amounts, and other asset types that you've added.
- The other table will show all credit cards that have been added to your account.

Below the second table, a `Net Total` textblock willd dynamically calculate your assets less credit card liabilities (i.e. net total).

At the bottom of this page is a form that will allow a user to create new accounts to add.
The default account types available include:
- Cash
- Checking Account
- Credit Card
- Digital Wallet (like Venmo, CashApp, or PayPal)
- Savings Account

Depending on the account type selected, additional form boxes will appear to gather relevant information. For example, if `Credit Card` is chosen, then you will also be prompted to provide the card's APR and the payment due date for each month.

### Returning User

After going through the initial setup and adding some accounts, you can access the following routes:
- Transactions
- Record Transactions
- IOU Log
- Gift Cards

On the top right of your window, you should also be able to `Manage Account` or `Log Out`.

#### Manage Account

On the `Manage Account` page, the user can view current transaction categories. This will start as an empty list but you can add categories by typing a category name and clicking the `Add Category` button. Once you've added at least 1 category, the `Transaction Categories` list will be populated by the categories you've created.

Similarly, users may add additional `Account Types`. This list starts pre-populated with some of the most common account types, but users are welcome to add more.

#### Gift Cards

The `Gift Cards` page includes a table (that starts empty) and form to enable users to add gift cards.
Simply fill out the `Company Name`, `Starting Balance`, and `Current Balance`, click `Add Gift Card`, and then the table on the page will be dynamically upated.

#### Record Transation

The `Record Transaction` page allows the user to record 1 of 5 different transaction types.

##### Expenses
This is probably the most common type of transaction where a user wants to record that they purchased something from a business. This can be a good or service, and the amount paid can even be negative to denote a refund. This form has a checkbox called `Gift Card Used?`. If this box is checked, the payment method box will change to show all non-zero-balance gift cards that have been added to the user's account. If the box is not checked, all the financial accounts that the user has added will be available to select from. Certain fields are required (both using frontend logic and backend checks). Once the user clicks the `Record Transation` button, they will be redirected to the `Transactions` page which will have been dynamically populated with the information that was entered.

##### Transfers
If the user selects the `Transfers` radio button at the top of the page, the form will dynamically change, providing input fields relevant to recording a money transfer transaction. Namely, asking for a `Source Account` and a `Destination Account`.


##### Credit Card Payments
If the user selects the `Pay Off Credit Card` radio button at the top of the page, the form will dynamically change, providing input fields relevant to recording a payment made on a credit card. Some backend logic will prevent a user from being able to select another credit card as the `Source Account`.


##### Recording An IOU
If the user selects the `Record IOU` radio button at the top of the page, the form will dynamically change, providing input fields relevant to recording an IOU. This supports the creation of an obligation towards someone else (Accounts Payable) or someone else's obligation to you (Accounts Receivable). Once a transaction is recorded, the user will be redirected to the IOU Log where these specific kinds of transactions may be viewed.


##### Paying Off An IOU
If the user selects the `Pay Off IOU` radio button at the top of the page, the form will dynamically change, providing input fields relevant to recording a payment towards an existing IOU obligation. This supports the user making a payment towards someone else (reducing or eliminating what they owe) or recording someone else having made a payment to the user (reducing what the user is owed by someone else). This "direction" of transaction is specified in the `Direction of IOU Payment` field. It's important to note that a person's name must be entered the same way each time in order to correctly link said person to all relevant IOU transactions. (e.g. Sending money to "P. Pete" will not reduce what you owe to "Pirate Pete")


#### Transactions

The `Transactions` page provides a comprehensive table view of all (non-IOU) transactions that have been recorded. It provides details like date, time, amount, item, category, and notes. It also shows the source account (also known as the payment method) and the target account (often a company, in the case of standard transaction). This table will show purchases, refunds, credit card payments, and transfers of money between accounts.

#### IOU Log

The `IOU Log` page provides a space for seeing who you owe money to and who owes money to you.
This is shown cumulatively in the top two tables. Below these first two tables is a dynamically calculated field that shows the `Net Owed`. The color will vary depending on if you owe more to others, others owe more to you, or if they are perfectly balanced.

The bottom tables showcase each individual transaction, first those centered around owing others, the final table showing transactions related to owing you.

## FUTURE IMPROVEMENTS

### Planned Additions
- Password complexity requirements
- Tables that support in-line editing and row deletion (similar to what the Gift Cards table supports at present)
- Dynamically sortable tables (for transactions, sort by amount, date, company, etc.)
- User-specified number of rows to show for a given table
- Sections for adding and tracking income
- Sections for adding and tracking savings (including savings goals, how much is currently set aside, how much total is needed, etc.)
- Ability to import CSV files with pre-existing data (namely transactions but would also likely support other tables; these imports would also allow the user to specify whether they want their current accounts to reflect all the new transactions or ignore them)
- Allow users to remove and reset default categories for expense types, account types, etc.
- Allow users to keep track of rewards earned on credit cards
- Allow users to utilize multiple forms of payment for a single transaction (Gift Card + Credit Card, for example)
- Payback dates for IOUs, if applicable

### Planned Modifications
- Switch backend DB from SQLite to PostgreSQL
- Enhanced site aesthetics