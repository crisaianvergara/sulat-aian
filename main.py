from flask import Flask, render_template, redirect, url_for, flash, abort
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bootstrap import Bootstrap
from forms import (
    LoginForm,
    RegisterForm,
    CreatePostForm,
    CommentForm,
    SubscriberForm,
    ContactForm,
)
from flask_ckeditor import CKEditor
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from datetime import datetime
from functools import wraps
from flask_gravatar import Gravatar
from flask_login import (
    UserMixin,
    login_user,
    LoginManager,
    login_required,
    current_user,
    logout_user,
    AnonymousUserMixin,
)
from sqlalchemy import desc
import smtplib
import os

# Flask App
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY")
Bootstrap(app)
ckeditor = CKEditor(app)

# Database
app.app_context().push()
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Table Users
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    posts = relationship("BlogPost", back_populates="author")

    comments = relationship("Comment", back_populates="comment_author")


# Table Blog Posts
class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    author = relationship("User", back_populates="posts")

    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    date = db.Column(db.String(250), nullable=False)

    comments = relationship("Comment", back_populates="parent_post")


# Table Comments
class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    comment_author = relationship("User", back_populates="comments")

    post_id = db.Column(db.Integer, db.ForeignKey("blog_posts.id"))
    parent_post = relationship("BlogPost", back_populates="comments")
    text = db.Column(db.Text, nullable=False)


class Subscribers(db.Model):
    __tablename__ = "subscribers"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)


# Gravatar
gravatar = Gravatar(
    app,
    size=100,
    rating="g",
    default="retro",
    force_default=False,
    force_lower=False,
    use_ssl=False,
    base_url=None,
)

# Anonymous User Default ID
class Anonymous(AnonymousUserMixin):
    def __init__(self):
        self.id = 0


# Logging In
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.anonymous_user = Anonymous


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Create admin-only decorator
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)

    return decorated_function


# My Info
MY_EMAIL = os.environ.get("MY_EMAIL_SUPER")
MY_PASSWORD = os.environ.get("MY_PASSWORD_YAHOO")
MY_NAME = os.environ.get("MY_NAME_YAHOO")
MY_RECIPIENT = os.environ.get("MY_RECIPIENT_YAHOO")


# Function Send Message
def send_message(name, email, phone, message):
    message = (
        f'From: "{MY_NAME}" <{MY_EMAIL}>\n'
        f"To: {MY_RECIPIENT}\n"
        f"Subject: Message From Your Website\n\n"
        f"Name: {name}\nEmail: {email}\nPhone: {phone}\nMessage: {message}".encode(
            "utf-8"
        )
    )

    with smtplib.SMTP("smtp.mail.yahoo.com", port=587) as connection:
        connection.starttls()
        connection.login(user=MY_EMAIL, password=MY_PASSWORD)
        connection.sendmail(from_addr=MY_EMAIL, to_addrs=MY_RECIPIENT, msg=message)


# Home
@app.route("/", methods=["GET", "POST"])
def home():
    form = SubscriberForm()
    posts = BlogPost.query.order_by(desc("id")).limit(3)
    limit_two = BlogPost.query.limit(2)
    # Subscriber
    if form.validate_on_submit():
        if Subscribers.query.filter_by(email=form.subscriber.data).first():
            flash("You've already subscribed with that email.", "red")
            return redirect(url_for("home"))
        new_subscriber = Subscribers(email=form.subscriber.data)
        db.session.add(new_subscriber)
        db.session.commit()
        flash("Subscribed successfully.", "green")
        return redirect(url_for("home"))
    return render_template(
        "index.html",
        posts=posts,
        current_user=current_user,
        limit_two=limit_two,
        form=form,
    )


# Admin Section
# New Post
@app.route("/new-post", methods=["GET", "POST"])
@admin_only
@login_required
def new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            author=current_user,
            title=form.title.data.title(),
            subtitle=form.subtitle.data.title(),
            img_url=form.img_url.data,
            body=form.body.data,
            date=datetime.today().strftime("%B %d, %Y"),
        )
        db.session.add(new_post)
        db.session.commit()
        flash("You're story successfully published.", "green")
        return redirect(url_for("home"))
    return render_template("make-post.html", form=form, current_user=current_user)


# View Post and Comment
@app.route("/view-post/<int:post_id>", methods=["GET", "POST"])
def view_post(post_id):
    form = CommentForm()
    requested_post = BlogPost.query.get_or_404(post_id)
    if form.validate_on_submit():
        if current_user.is_authenticated:
            new_comment = Comment(
                text=form.comment.data,
                comment_author=current_user,
                parent_post=requested_post,
            )
            db.session.add(new_comment)
            db.session.commit()
            flash("Commented successfully.", "green")
            return redirect(url_for("view_post", post_id=post_id))
        flash("You need to sign in or sign up to comment.", "red")
        return redirect(url_for("view_post", post_id=post_id))

    return render_template(
        "view-post.html",
        post=requested_post,
        current_user=current_user,
        form=form,
    )


# Edit Post
@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
@login_required
def edit_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=current_user,
        body=post.body,
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.body = edit_form.body.data
        db.session.commit()
        flash("Post successfully edited.", "green")
        return redirect(url_for("view_post", post_id=post.id))
    return render_template(
        "make-post.html",
        form=edit_form,
        is_edit=True,
        current_user=current_user,
        post_id=post_id,
    )


# Delete Post
@app.route("/delete/<int:post_id>")
@admin_only
def delete(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    flash("Post successfully deleted.", "green")
    return redirect(url_for("home"))


# Admin, Users, And Guest Section
# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        if not user:
            flash("That email does not exist, please try again.", "red")
            return redirect(url_for("login"))
        elif not check_password_hash(user.password, password):
            flash("Password incorrect, please try again.", "red")
            return redirect(url_for("login"))
        else:
            login_user(user)
            flash("You've successfully signed in.", "green")
            return redirect(url_for("home"))
    return render_template("login.html", form=form, current_user=current_user)


# Logout
@app.route("/logout")
def logout():
    logout_user()
    flash("You've successfully signed out.", "green")
    return redirect(url_for("home"))


# Register
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash("You've already signed up with that email, log in instead.", "red")
            return redirect(url_for("register"))
        hash_and_salted_password = generate_password_hash(
            form.password.data, method="pbkdf2:sha256", salt_length=8
        )
        new_user = User(
            name=form.name.data,
            email=form.email.data,
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        flash("You've successfully signed up.", "green")
        return redirect(url_for("home"))
    return render_template("register.html", form=form, current_user=current_user)


# Blog
@app.route("/blog")
def blog():
    posts = BlogPost.query.order_by(desc("id"))
    return render_template("blog.html", posts=posts)


# About
@app.route("/about")
def about():
    return render_template("about.html")


# Contact
@app.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        send_message(
            form.name.data, form.email.data, form.phone_number.data, form.message.data
        )
        flash("Message sent.", "green")
        return redirect(url_for("contact"))
    return render_template("contact.html", form=form)


# Run Flask
if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
