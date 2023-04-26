import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv

from db_models import db
from routes import register_routes
from vectorstores import register_vectorstores
from utils import add_core_tool
from core_tools import long_term_memory_tool
import crypto_utils

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///conversations.db'
db.init_app(app)
CORS(app)


if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    register_vectorstores(app)
    print(app.vectorstores)


add_core_tool(app, long_term_memory_tool)

register_routes(app)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5005, use_reloader=False)

    
