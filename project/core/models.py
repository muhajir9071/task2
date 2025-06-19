from mongoengine import Document, StringField, ReferenceField, DateTimeField
from users.models import User
from datetime import datetime

class Project(Document):
    title = StringField(required=True)
    description = StringField()
    created_at = DateTimeField(default=datetime.utcnow)
    owner = ReferenceField(User, required=True)

    meta = {
        'collection': 'projects',
        'ordering': ['-created_at']
    }

class Task(Document):
    project = ReferenceField(Project, required=True)
    title = StringField(required=True)
    description = StringField()
    status = StringField(
        choices=["ToDo", "InProgress", "Done"],
        default="ToDo"
    )
    due_date = DateTimeField()
    created_at = DateTimeField(default=datetime.utcnow)
    assigned_to = ReferenceField(User, required=False, null=True)

    meta = {
        'collection': 'tasks',
        'ordering': ['-created_at']
    }






