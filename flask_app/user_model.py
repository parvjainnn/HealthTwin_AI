"""Flask-Login User model wrapper."""
from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, data: dict):
        self.id = data['id']
        self.username = data['username']
        self.email = data['email']
        self.password_hash = data['password_hash']
        self.created_at = data.get('created_at', '')

    def get_id(self):
        return str(self.id)
