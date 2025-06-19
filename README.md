# Task Management System (Django + MongoDB + DRF)

A simple backend API for managing tasks and projects, using:
- Django (latest)
- Django REST Framework
- MongoDB (via MongoEngine)
- Custom Token Authentication 

## 🔧 Features

- User Registration, Login, Logout
- Create, Read, Update, Delete (CRUD) for:
  - Projects
  - Tasks
- Filter tasks by status/project/user
- Custom Token Authentication 
- Clean beginner-friendly code

## 🚀 Getting Started

```bash
# Clone the repository
git clone https://github.com/muhajir9071/task2.git
cd task2

# Create and activate virtual environment
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python manage.py runserver
