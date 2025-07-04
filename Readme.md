# Expense-Trac-Vrit API Documentation

Expense-Trac-Vrit is a **RESTful API** for managing user **authentication**, **income**, and **expense records**. Built with **Django**, it offers secure JWT-based authentication and CRUD operations for financial management with pagination and tax handling.

---

## ✨ Overview

* **Backend**: Django
* **Auth**: JWT (SimpleJWT)
* **Data Types**: JSON, Form Data
* **Base URL**: `http://127.0.0.1:8000`

---

## 📄 Table of Contents

1. [Setup](#setup)
2. [Authentication](#authentication)

   * Register
   * Login
   * Logout
   * Refresh Token
3. [Income Management](#income-management)
4. [Expense Management](#expense-management)
5. [Health Check](#health-check)
6. [Notes](#notes)

---

## ⚙️ Setup

### Prerequisites

* Python 3.8+
* Django 3.2+
* Django REST Framework
* PostgreSQL (or any supported DB)
* Postman (for API testing)

### Installation

```bash
git clone <repository-url>
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cd expense-trac-vrit
```

### Migrations & Run

```bash
python manage.py migrate
python manage.py runserver
```

---

## 🔐 Authentication

### 1. Register User

**POST** `/user/api/auth/register/`

```json
{
  "name": "ujwal",
  "email": "ujwal@example.com",
  "password": "123456"
}
```

**Response:**

```json
{
  "message": "User registered successfully.",
  "username": "ujwal",
  "email": "ujwal@example.com"
}
```

### 2. Login User

**POST** `/user/api/auth/login/`

```json
{
  "name": "ujwal",
  "password": "123456"
}
```

**Response:**

```json
{
  "message": "Login successful",
  "access": "<access_token>",
  "refresh": "<refresh_token>"
}
```

### 3. Logout User

**POST** `/user/api/auth/logout/`

```json
{
  "refresh": "<refresh_token>"
}
```

**Response:**

```json
{
  "message": "User logged out and token blacklisted."
}
```

### 4. Refresh Token

**POST** `/user/api/auth/refresh/`

```json
{
  "refresh": "<refresh_token>"
}
```

**Response:**

```json
{
  "access": "<new_access_token>"
}
```

---

## 💸 Income Management

### 1. Create Income

**POST** `/income/api/setIncome/`

```json
{
  "name": "Salary",
  "amount": 1000.00,
  "source": "Bank",
  "date": "2025-07-04",
  "tax": 100.00,
  "tax_type": "flat",
  "transaction_type": "credit",
  "notes": "July salary"
}
```

**Success Response:** `201 Created`

### 2. Get All Incomes

**GET** `/income/api/getAllIncomes/?page=1&per_page=5`
**Response:**

```json
{
  "count": 50,
  "results": [ { "id": 1, ... } ]
}
```

### 3. Get Income by ID

**GET** `/income/api/getIncomeById/?id=3`

### 4. Edit Income

**PUT** `/income/api/editIncome/`

```json
{
  "id": 1,
  "name": "Updated Salary",
  "amount": 1200.00,
  "source": "Bank",
  "date": "2025-07-05",
  "tax": 120.00,
  "tax_type": "flat",
  "transaction_type": "credit",
  "notes": "Updated note"
}
```

### 5. Delete Income

**DELETE** `/income/api/deleteIncome/`

```json
{
  "id": 1
}
```

---

## 💳 Expense Management

### 1. Create Expense

**POST** `/expense/api/setExpense/`

```json
{
  "title": "Groceries",
  "description": "Weekly shopping",
  "amount": 100.00,
  "source": "Cash",
  "date": "2025-07-04",
  "tax": 10.00,
  "tax_type": "flat",
  "transaction_type": "debit"
}
```

### 2. Get All Expenses

**GET** `/expense/api/getAllExpense/?page=1&per_page=5`

### 3. Get Expense by ID

**GET** `/expense/api/getExpenseById/?id=2`

### 4. Edit Expense

**PUT** `/expense/api/editExpense/`

```json
{
  "id": 1,
  "title": "Groceries",
  "description": "Updated shopping",
  "amount": 120.00,
  "source": "Cash",
  "date": "2025-07-06",
  "tax": 12.00,
  "tax_type": "flat",
  "transaction_type": "debit"
}
```

### 5. Delete Expense

**DELETE** `/expense/api/deleteExpense/`

```json
{
  "id": 1
}
```

---

## ❤️ Health Check

**GET** `/`
**Response:**

```json
{
  "message": "Server is running"
}
```

---

## 🔹 Notes

* **Auth Header**: Use `Bearer <access_token>` for protected routes.
* **Date Format**: `YYYY-MM-DD`
* **Tax Calculation:**

  * `flat` → `total = amount + tax`
  * `percentage` → `total = amount + (amount * tax / 100)`
* **Content-Type:**

  * JSON for most requests
  * `x-www-form-urlencoded` for form data

---

## 🎉 Happy Coding!

For any issues or contributions, feel free to fork or raise an issue on the repository.
