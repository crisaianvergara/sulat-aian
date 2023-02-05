from flask import render_template, redirect, url_for, flash, abort
from blogproject import app, db
from blogproject.models import User, BlogPost, Comment, Subscriber
from werkzeug.security import generate_password_hash, check_password_hash
from blogproject.forms import (
    LoginForm,
    RegisterForm,
    CreatePostForm,
    CommentForm,
    SubscriberForm,
    ContactForm,
)
from datetime import datetime
from functools import wraps
from flask_login import (
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
from flask_gravatar import Gravatar
from flask_ckeditor import CKEditor

# CkEditor
ckeditor = CKEditor(app)

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


# Flask Login
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
def send_message(name, email, phone, message, recipient):
    if message == "notify":
        message = (
            f'From: "{MY_NAME}" <{MY_EMAIL}>\n'
            f"To: {recipient}\n"
            f"Subject: New Blog Alert!\n\n"
            f"I have published a new blog post. It's packed with valuable insights and information. Check it out.".encode(
                "utf-8"
            )
        )
    else:
        message = (
            f'From: "{MY_NAME}" <{MY_EMAIL}>\n'
            f"To: {recipient}\n"
            f"Subject: Message From Your Website\n\n"
            f"Name: {name}\nEmail: {email}\nPhone: {phone}\nMessage: {message}".encode(
                "utf-8"
            )
        )

    with smtplib.SMTP("smtp.mail.yahoo.com", port=587) as connection:
        connection.starttls()
        connection.login(user=MY_EMAIL, password=MY_PASSWORD)
        connection.sendmail(from_addr=MY_EMAIL, to_addrs=recipient, msg=message)


# Home
@app.route("/home", methods=["GET", "POST"])
@app.route("/", methods=["GET", "POST"])
def home():
    form = SubscriberForm()
    posts = BlogPost.query.order_by(desc("id")).limit(3)
    limit_two = BlogPost.query.limit(2)
    # Subscriber
    if form.validate_on_submit():
        if Subscriber.query.filter_by(email=form.subscriber.data).first():
            flash("You've already subscribed with that email.", "info")
            return redirect(url_for("home"))
        new_subscriber = Subscriber(email=form.subscriber.data)
        db.session.add(new_subscriber)
        db.session.commit()
        flash("Subscribed successfully.", "success")
        return redirect(url_for("home"))
    return render_template(
        "index.html",
        posts=posts,
        current_user=current_user,
        limit_two=limit_two,
        form=form,
    )


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
        # Notify Subscribers
        subscribers = Subscriber.query.all()
        for subscriber in subscribers:
            send_message("", "", "", "notify", subscriber.email)
        flash("You're story successfully published.", "success")
        return redirect(url_for("home"))
    return render_template(
        "make-post.html", form=form, current_user=current_user, title="New Post"
    )


# View Post and Comments
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
            flash("Commented successfully.", "success")
            return redirect(url_for("view_post", post_id=post_id))
        flash("You need to sign in or sign up to comment.", "danger")
        return redirect(url_for("view_post", post_id=post_id))

    return render_template(
        "view-post.html",
        post=requested_post,
        current_user=current_user,
        form=form,
        title="View Post",
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
        flash("Post successfully edited.", "success")
        return redirect(url_for("view_post", post_id=post.id))
    return render_template(
        "make-post.html",
        form=edit_form,
        is_edit=True,
        current_user=current_user,
        post_id=post_id,
        title="Edit Post",
    )


# Delete Post
@app.route("/delete/<int:post_id>")
@admin_only
def delete(post_id):
    post_to_delete = BlogPost.query.get_or_404(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    flash("Post successfully deleted.", "success")
    return redirect(url_for("home"))


# Delete Comment
@app.route("/delete-comment/<int:comment_id>/<post_id>")
def delete_comment(comment_id, post_id):
    comment_to_delete = Comment.query.get_or_404(comment_id)
    db.session.delete(comment_to_delete)
    db.session.commit()
    flash("Comment successfully deleted.", "success")
    return redirect(url_for("view_post", post_id=post_id))


# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        if not user:
            flash("That email does not exist, please try again.", "danger")
            return redirect(url_for("login"))
        elif not check_password_hash(user.password, password):
            flash("Password incorrect, please try again.", "danger")
            return redirect(url_for("login"))
        else:
            login_user(user)
            flash("You've successfully signed in.", "success")
            return redirect(url_for("home"))
    return render_template(
        "login.html", form=form, current_user=current_user, title="Sign In"
    )


# Logout
@app.route("/logout")
def logout():
    logout_user()
    flash("You've successfully signed out.", "success")
    return redirect(url_for("login"))


# Register
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash("You've already signed up with that email, log in instead.", "info")
            return redirect(url_for("login"))
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
        flash("You've successfully signed up.", "success")
        return redirect(url_for("home"))
    return render_template(
        "register.html", form=form, current_user=current_user, title="Sign Up"
    )


# Blog
@app.route("/blog")
def blog():
    posts = BlogPost.query.order_by(desc("id"))
    return render_template("blog.html", posts=posts, title="Blog")


# About
@app.route("/about")
def about():
    return render_template("about.html", title="About")


# Contact
@app.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        send_message(
            form.name.data,
            form.email.data,
            form.phone_number.data,
            form.message.data,
            MY_RECIPIENT,
        )
        flash("Message sent.", "success")
        return redirect(url_for("contact"))
    return render_template("contact.html", form=form, title="Contact")
