import uuid
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Conversation(db.Model):
    id = db.Column(db.String(36),
                   primary_key=True,
                   default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(255), nullable=False)
    model = db.Column(db.String(50), nullable=True)
    messages = db.relationship('Message', backref='conversation', lazy=True)


class Message(db.Model):
    id = db.Column(db.String(36),
                   primary_key=True,
                   default=lambda: str(uuid.uuid4()))
    sender = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.String(255), nullable=False)
    conversation_id = db.Column(db.String(36),
                                db.ForeignKey('conversation.id'),
                                nullable=False)
