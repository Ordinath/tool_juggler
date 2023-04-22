import uuid
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import JSON
import os

db = SQLAlchemy()


class Conversation(db.Model):
    id = db.Column(db.String(36),
                   primary_key=True,
                   default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(255), nullable=False)
    model = db.Column(db.String(50), nullable=True)
    embedded = db.Column(db.Boolean, nullable=False, default=False)
    embeddings = db.relationship(
        'Embedding', backref='conversation', lazy=True)
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


class Embedding(db.Model):
    id = db.Column(db.String(36),
                   primary_key=True,
                   default=lambda: str(uuid.uuid4()))
    # Add any additional columns you need for the Embedding model
    conversation_id = db.Column(db.String(36),
                                db.ForeignKey('conversation.id'),
                                nullable=False)


class Tool(db.Model):
    id = db.Column(db.String(36),
                   primary_key=True,
                   default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False, unique=True)
    enabled = db.Column(db.Boolean, nullable=False, default=True)
    core = db.Column(db.Boolean, nullable=False, default=False)
    tool_type = db.Column(db.String(50), nullable=False)
    tool_definition_path = db.Column(db.String(255), nullable=False)
    manifest = db.Column(JSON, nullable=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=True,
                           onupdate=datetime.utcnow)

