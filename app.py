import os
from flask import Flask, request, render_template, jsonify, redirect, url_for, session
import joblib
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
from datetime import datetime
from models import db, User, Prediction  # Import models from models.py

app = Flask(__name__)
csrf = CSRFProtect(app)
app.secret_key = os.urandom(24)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'news_predictions.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize DB
db.init_app(app)
migrate = Migrate(app, db)

# Load model and vectorizer
try:
    model_path = os.path.join(basedir, "fake_news_model.pkl")
    vectorizer_path = os.path.join(basedir, "vectorizer.pkl")
    model = joblib.load(model_path)
    vectorizer = joblib.load(vectorizer_path)
except FileNotFoundError:
    print(f"Error: Model files not found in {basedir}")
    exit()
except Exception as e:
    print(f"Error loading models: {e}")
    exit()

# Prediction function
def predict_fake_news(news_text):
    try:
        transformed_text = vectorizer.transform([news_text])
        prediction = model.predict(transformed_text)[0]
        return "Fake News" if prediction == 0 else "Real News"
    except Exception as e:
        print(f"Error during prediction: {e}")
        return "Error during prediction"

# Forms
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class SignupForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Confirm Password')
    submit = SubmitField('Sign Up')

# Routes
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/check_session")
def check_session():
    return jsonify({"logged_in": 'user_id' in session})

@app.route("/analyze", methods=["GET", "POST"])
def analyze():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        news_text = request.form.get("news", "")
        if news_text:
            result = predict_fake_news(news_text)
            if result == "Error during prediction":
                return jsonify({"error": "An error occurred during analysis."}), 500

            new_prediction = Prediction(news_text=news_text, prediction=result, user_id=session['user_id'])
            db.session.add(new_prediction)
            db.session.commit()

            return jsonify({"prediction": result})

    return render_template("analyze.html")

@app.route("/predictions")
def get_predictions():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    predictions = Prediction.query.filter_by(user_id=user_id).order_by(Prediction.prediction_date.desc()).limit(5).all()

    return jsonify([
        {
            "news_text": p.news_text,
            "prediction": p.prediction,
            "date": p.prediction_date.isoformat()
        }
        for p in predictions
    ])

@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()  # Create an instance of LoginForm

    if request.method == "POST":
        if request.content_type != "application/json":
            return jsonify({"success": False, "message": "Invalid request format."}), 400

        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return jsonify({"success": True, "redirect": url_for('analyze')})

        return jsonify({"success": False, "message": "Invalid email or password."})

    return render_template("login.html", form=form)  


@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        if User.query.filter_by(email=email).first():
            return jsonify({"error": True, "message": "Email already exists"})

        new_user = User(email=email, password=generate_password_hash(password, method='pbkdf2:sha256'))
        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": True, "message": f"Error during signup: {str(e)}"})

    return render_template("signup.html", form=form)

@app.route("/logout", methods=["POST"])
def logout():
    session.pop('user_id', None)
    return jsonify({"success": True, "redirect": url_for('index')})  # ✅ Return JSON response


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
