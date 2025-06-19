# users/models.py

from mongoengine import Document, StringField
import uuid

class User(Document):
    username = StringField(required=True, unique=True)
    email    = StringField(required=True, unique=True)
    password = StringField(required=True)

class Token(Document):
    user_id = StringField(required=True)                                    # store User.id (as str)
    key     = StringField(
        required=True,
        unique=True,
        default=lambda: str(uuid.uuid4())                                   # always non-null
    )



