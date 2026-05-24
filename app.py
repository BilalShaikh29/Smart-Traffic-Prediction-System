from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import pickle
import numpy as np

app = Flask(__name__)

# Secret key
app.secret_key = "traffic_project_key"

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"

db = SQLAlchemy(app)

bcrypt = Bcrypt(app)

# Load trained model
model = pickle.load(
    open("models/traffic_model.pkl", "rb")
)


# User table
class User(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(100),
        unique=True
    )

    password = db.Column(
        db.String(200)
    )


# Create database
with app.app_context():
    db.create_all()


# Home
@app.route("/")
def home():

    return redirect("/login")


# Register
@app.route("/register", methods=["GET","POST"])
def register():

    if request.method=="POST":

        username=request.form["username"]

        password=bcrypt.generate_password_hash(
            request.form["password"]
        ).decode("utf-8")

        new_user=User(
            username=username,
            password=password
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect("/login")

    return render_template("register.html")


# Login
@app.route("/login", methods=["GET","POST"])
def login():

    if request.method=="POST":

        username=request.form["username"]

        password=request.form["password"]

        user=User.query.filter_by(
            username=username
        ).first()

        if user and bcrypt.check_password_hash(
            user.password,
            password
        ):

            session["user"]=username

            return redirect("/dashboard")

    return render_template("login.html")


# Dashboard
@app.route("/dashboard")
def dashboard():

    if "user" not in session:

        return redirect("/login")

    return render_template(
        "dashboard.html",
        username=session["user"]
    )


# Prediction page + prediction processing
@app.route("/predict", methods=["GET","POST"])
def predict():

    if "user" not in session:

        return redirect("/login")

    # Open prediction page
    if request.method=="GET":

        return render_template(
            "index.html"
        )


    # Receive form data
    Junction=int(
        request.form["Junction"]
    )

    Year=int(
        request.form["Year"]
    )

    Month=int(
        request.form["Month"]
    )

    Day=int(
        request.form["Day"]
    )

    Hour=int(
        request.form["Hour"]
    )

    DayOfWeek=int(
        request.form["DayOfWeek"]
    )


    features=np.array([
        [
            Junction,
            Year,
            Month,
            Day,
            Hour,
            DayOfWeek
        ]
    ])


    prediction=round(
        model.predict(features)[0]
    )


    if prediction<=20:

        status="Low Traffic"

    elif prediction<=50:

        status="Medium Traffic"

    else:

        status="High Traffic"


    return render_template(
        "result.html",
        prediction=prediction,
        status=status
    )


# Logout
@app.route("/logout")
def logout():

    session.pop(
        "user",
        None
    )

    return redirect("/login")


if __name__=="__main__":

    app.run(debug=True)