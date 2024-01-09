from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# Flask App
app = Flask(__name__)

# Secret Key
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY")

app.app_context().push()

# Database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL_SULAT")

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Routes
from blogproject import routes
