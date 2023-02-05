from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# Flask App
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY")

# Database
app.app_context().push()
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Routes
from blogproject import routes
