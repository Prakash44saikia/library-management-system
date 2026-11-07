# Library Management System

A web-based library management system built with Django. Librarians manage the book catalog and issue and return books, and members browse books and track what they have borrowed, including due dates and fines.

**Live demo:** https://prakashsaikia002gmailcom.pythonanywhere.com

## Features

**Librarian**
- Add, edit and delete books, with categories and stock counts
- Issue books to members (14-day loan period)
- Mark books as returned; stock updates automatically
- Dashboard with total titles, issued books, overdue books and member count
- Overdue list with automatically calculated fines (Rs. 2 per day)

**Member**
- Sign up and log in
- Search the catalog by title, author or ISBN, and filter by category
- See books currently borrowed, due dates, fines and borrowing history

**General**
- Role-based access: only staff can add, edit, delete, issue or return
- Duplicate-issue protection and out-of-stock handling
- Responsive layout that works on phones and laptops

## Tech stack

- Python 3.11, Django 5.2
- SQLite database
- Bootstrap 5
- Hosted on PythonAnywhere

## Screenshots

| Login | Librarian dashboard |
|---|---|
| ![Login](screenshots/login.png) | ![Dashboard](screenshots/dashboard.png) |

| Book catalog with search | Issue a book |
|---|---|
| ![Catalog](screenshots/catalog.png) | ![Issue](screenshots/issue.png) |

| Issued books and fines | Member view on mobile |
|---|---|
| ![Issued](screenshots/issued.png) | ![Mobile](screenshots/mobile.png) |

## Run it locally

```bash
git clone https://github.com/Prakash44saikia/library-management-system.git
cd library-management-system
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Then open http://127.0.0.1:8000/ and log in with the superuser you created. Staff accounts see the librarian features, and users who sign up through the site are members.

## Project structure

```
library_project/   project settings and root URLs
library/           models, views, forms, URLs, templates
  models.py        Category, Book, Member, Issue
  views.py         catalog, search, issue/return, dashboard
  templates/       Bootstrap pages
```

## Data model

- **Category**: name
- **Book**: title, author, ISBN, category, total and available copies
- **Member**: linked one-to-one to a Django user
- **Issue**: book, member, issue date, due date, return date; the fine is calculated from the days late

## Demo access

Use the live link above. Login details for the demo are shared separately.

## Author

Prakash Saikia