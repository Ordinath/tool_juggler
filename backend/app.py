
from flask import Flask, g
from flask_cors import CORS
from dotenv import load_dotenv

from db_models import db
from routes import register_routes
from handlers import register_handlers

import crypto_utils

load_dotenv()


app = Flask(__name__)
app.config.from_object('config')

db.init_app(app)
with app.app_context():
    db.create_all()
CORS(app)

# we have to transfer this logic on the after login stage:

# register_vectorstores(app)
# print(app.vectorstores)
# add_core_tool(app, long_term_memory_tool)
# add_secret_if_not_exists(app, "OPENAI_API_KEY", "TO_BE_PROVIDED")
register_handlers(app)
register_routes(app)

if __name__ == '__main__':
    app.run(debug=False, use_reloader=False)
