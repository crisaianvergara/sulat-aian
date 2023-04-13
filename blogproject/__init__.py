from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# Flask App
app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY")

# postgres://sulat_aian_user:BaaCICVYLsHJNrhi95F5Yxe3FpXoiREP@dpg-cgs46d02qv20m9nfebug-a.oregon-postgres.render.com/sulat_aian

# Database
app.app_context().push()

# Local
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"

# Render
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL_SULAT")

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Routes
from blogproject import routes
