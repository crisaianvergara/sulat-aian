from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, validators, TextAreaField
from wtforms.validators import DataRequired, Email, URL
from flask_ckeditor import CKEditorField

# Login Form
class LoginForm(FlaskForm):
    email = StringField(
        "Email Address",
        validators=[DataRequired(), Email()],
        render_kw={"placeholder": "Enter your email address"},
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired(), validators.Length(min=8, max=20)],
        render_kw={"placeholder": "Enter your password"},
    )
    submit = SubmitField("Sign In")


# Register Form
class RegisterForm(FlaskForm):
    name = StringField(
        "Name",
        validators=[DataRequired(), validators.length(min=3, max=50)],
        render_kw={"placeholder": "Enter your name"},
    )
    email = StringField(
        "Email Address",
        validators=[DataRequired(), Email()],
        render_kw={"placeholder": "Enter your email address"},
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired(), validators.Length(min=8, max=20)],
        render_kw={"placeholder": "Enter your password"},
    )
    submit = SubmitField("Sign Up")


# Create Post Form
class CreatePostForm(FlaskForm):
    title = StringField(
        "Post Title", validators=[DataRequired(), validators.length(min=5)]
    )
    subtitle = StringField(
        "Post Subtitle", validators=[DataRequired(), validators.Length(min=5)]
    )
    img_url = StringField("Post Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField(
        "Post Content", validators=[DataRequired(), validators.Length(min=50)]
    )
    submit = SubmitField("Publish")


# Comment Form
class CommentForm(FlaskForm):
    comment = StringField(
        "Comment",
        validators=[DataRequired()],
        render_kw={"placeholder": "Add a comment"},
    )
    submit = SubmitField("Comment")


class SubscriberForm(FlaskForm):
    subscriber = StringField(
        "Email Address",
        validators=[DataRequired(), Email()],
        render_kw={"placeholder": "Enter your email"},
    )


# Contact Form
class ContactForm(FlaskForm):
    name = StringField(
        "Full Name", validators=[DataRequired(), validators.length(min=5, max=50)]
    )
    email = StringField("Email Address", validators=[DataRequired(), Email()])
    phone_number = StringField("Phone Number", validators=[DataRequired()])
    message = TextAreaField("Your Message", validators=[DataRequired()])
