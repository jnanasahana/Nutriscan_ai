# FILE: app.py
from flask import Flask, render_template, redirect, url_for, flash, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
from PIL import Image
import pytesseract
import os
import io
import re
import time

# ---------- Flask Setup ----------
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "supersecretkey")

# ---------- Database Setup ----------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ---------- Login Manager ----------
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

# ---------- User Model ----------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ---------- Uploads Setup ----------
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'wedp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ---------- Ingredient Health Impact DB ----------
ingredientImpactDB = {
    "sugar":"High","salt":"High","trans fat":"High","butter":"High","margarine":"High",
    "processed meat":"High","mayonnaise":"High","white bread":"High","ice cream":"High",
    "chocolate syrup":"High","cream":"High","donuts":"High","candy":"High",
    "honey":"Moderate","flour":"Moderate","soy lecithin":"Moderate","corn syrup":"Moderate",
    "almond milk":"Moderate","yogurt":"Moderate","cheese":"Moderate","rice":"Moderate",
    "pasta":"Moderate","peanut butter":"Moderate","oatmeal":"Moderate","milk chocolate":"Moderate",
    "olive oil":"Low","milk":"Low","cocoa":"Low","vegetables":"Low","fruits":"Low",
    "nuts":"Low","whole grains":"Low","chicken breast":"Low","fish":"Low","tofu":"Low"
}

# ---------- Sample Data ----------
class ScanHistory:
    def __init__(self, productName, ingredients, healthReport, warnings, recommendations, timestamp):
        self.analysis = type("Analysis", (), {})()
        self.analysis.productName = productName
        self.analysis.ingredients = ingredients
        self.analysis.healthReport = healthReport
        self.analysis.warnings = warnings
        self.analysis.recommendations = recommendations
        self.timestamp = timestamp

history_data = [
    ScanHistory(
        productName="Chocolate Bar",
        ingredients=["Sugar", "Cocoa", "Milk"],
        healthReport="<p>High in sugar and calories</p>",
        warnings=[{"ingredient": "Sugar", "level": "High", "concern": "May affect blood sugar"}],
        recommendations=[{"name": "Dark Chocolate", "reason": "Less sugar", "benefits": "Better for health"}],
        timestamp=datetime.now()
    ),
    ScanHistory(
        productName="Granola Bar",
        ingredients=["Oats", "Honey", "Nuts"],
        healthReport="<p>Good source of fiber</p>",
        warnings=[],
        recommendations=[{"name": "Add more nuts", "reason": "Increase protein", "benefits": "Muscle health"}],
        timestamp=datetime.now()
    )
]

insights_data = [
    {"title": "Reduce Sugar Intake", "description": "Frequent consumption of high-sugar foods. Reduce them."},
    {"title": "Increase Fiber", "description": "Add vegetables and whole grains to improve digestion."}
]

goals_data = [
    {"title": "Increase Protein", "description": "Include lean meats, eggs, and legumes."},
    {"title": "Reduce Sugar", "description": "Avoid sugary drinks and snacks."},
    {"title": "Drink Water", "description": "Stay hydrated with 2-3 liters daily."}
]

# ---------- Helper: process_ingredients (from earlier convo) ----------
def process_ingredients(ingrdts, fdAdtv, chkCat, catldt):
    """Returns unique additive names found in ingrdts and a dict of categories found.
    ingrdts: iterable of ingredient strings
    fdAdtv: dict mapping additive identifier -> additive name/value
    chkCat: dict mapping category -> bool (whether to check)
    catldt: dict mapping category -> iterable of strings that belong to that category
    """
    results = []
    seen = set()
    hasCategory = {k: False for k in chkCat}

    for ing in ingrdts:
        normalized = ing.strip()
        # check additives dict by exact match or lowercased
        for key, value in fdAdtv.items():
            if normalized == key or normalized.lower() == key.lower():
                if value not in seen:
                    seen.add(value)
                    results.append(value)
        # check categories
        for k, check in chkCat.items():
            if check:
                for p in catldt.get(k, []):
                    if normalized == p or normalized.lower() == str(p).lower():
                        hasCategory[k] = True
                        break

    return results, hasCategory

# ---------- Routes ----------
@app.route("/")
def index():
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        email = (request.form.get("email") or "").strip()
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        if not username or not email or not password:
            flash("All fields are required.", "danger")
            return redirect(url_for("register"))
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("register"))
        if User.query.filter_by(username=username).first():
            flash("Username already taken.", "warning")
            return redirect(url_for("register"))
        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "warning")
            return redirect(url_for("login"))
        new_user = User(
            username=username,
            email=email,
            password=generate_password_hash(password, method="pbkdf2:sha256")
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Account created successfully. Please log in.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        identifier = request.form.get("identifier").strip()
        password = request.form.get("password")
        user = User.query.filter((User.username == identifier) | (User.email == identifier)).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials.", "danger")
            return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", current_user=current_user)

@app.route("/food-scan", methods=["GET", "POST"])
@login_required
def food_scan():
    if request.method == "POST":
        file = request.files.get('image')
        if not file or file.filename == "":
            flash("No image received. Please upload or capture an image.", "danger")
            return redirect(url_for("food_scan"))

        filename = secure_filename(file.filename or f"capture_{int(time.time())}.png")

        # If no extension, append .png
        if '.' not in filename:
            filename = f"{filename}.png"

        if not allowed_file(filename):
            flash("Invalid file type. Allowed: png, jpg, jpeg.", "danger")
            return redirect(url_for("food_scan"))

        # avoid overwriting: prepend timestamp
        filename = f"{int(time.time())}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # OCR
        extracted_text = ""
        try:
            img = Image.open(filepath)
            extracted_text = pytesseract.image_to_string(img)
        except Exception as e:
            # keep the exception message for debugging but don't show raw to user
            print("OCR error:", e)
            flash("OCR failed (is Tesseract installed?). Proceeding without OCR text.", "warning")

        # Tokenize ingredients
        tokens = [t.strip() for t in re.split(r"[\n,;:\(\)]+", extracted_text) if t.strip()]
        detected_ingredients = tokens or ["(No readable text)"]

        # ---------- Build Ingredient Impacts ----------
        ingredient_impacts = []
        health_summary = []
        high_count = 0
        recommendations = []

        for ing in detected_ingredients:
            impact = ingredientImpactDB.get(ing.lower(), "Moderate")
            ingredient_impacts.append({"ingredient": ing, "impact": impact})
            if impact == "High":
                high_count += 1
                recommendations.append({
                    "name": f"Lower-sugar alternative to {ing.title()}",
                    "label": "Better Choice",
                    "calories": 150,
                    "protein": 5,
                    "carbs": 18,
                    "fat": 6,
                    "sodium": 80,
                    "reason": f"Reduce {ing}",
                    "benefits": "Better for health"
                })

        health_summary.append(f"{high_count} high impact ingredient(s) detected.")

        # Sample nutrition and product info
        product_info = {"name": "Sample Product", "brand": "Demo Brand", "label": "Moderate Health Risk"}
        nutrition = {"Calories": 250, "Protein (g)": 8, "Carbs (g)": 35, "Fat (g)": 10, "Sodium (mg)": 200}

        return render_template(
            "result.html",
            current_user=current_user,
            image_file=filename,
            extracted_text=extracted_text,
            ingredient_impacts=ingredient_impacts,
            health_summary=health_summary,
            recommendations=recommendations,
            product_info=product_info,
            nutrition=nutrition
        )

    return render_template("food_scan.html", current_user=current_user)

@app.route("/nutrition-history")
@login_required
def nutrition_history():
    return render_template("nutrition_history.html", current_user=current_user, history=history_data)

# ---------- Health Insights & Diet Goals (works for authenticated and anonymous users) ----------
@app.route("/health-insights")
def health_insights():
    if current_user.is_authenticated:
        user_insights = insights_data
        if not user_insights:
            user_insights = [{"title": "No insights yet", "description": "Start logging your meals and activity to get insights."}]
    else:
        user_insights = [
            {"title": "Stay Active", "description": "Try to walk at least 30 minutes daily."},
            {"title": "Balanced Diet", "description": "Include a mix of protein, carbs, and healthy fats."},
            {"title": "Hydration", "description": "Drink at least 2-3 liters of water daily."}
        ]
    return render_template("health_insights.html", health_insights=user_insights)

@app.route("/diet-goals")
def diet_goals():
    if current_user.is_authenticated:
        user_goals = goals_data
        if not user_goals:
            user_goals = [{"title": "No goals set", "description": "Set your diet goals to get started."}]
    else:
        user_goals = goals_data
    return render_template("diet_goals.html", goals=user_goals)

@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html", current_user=current_user)

@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html', current_user=current_user)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route('/uploads/<path:filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ---------- Initialize DB ----------
with app.app_context():
    db.create_all()

# ---------- Run ----------
if __name__ == "__main__":
    # Helpful debug information
    print("Starting NutriScan app. Make sure Tesseract OCR is installed and on PATH. Example: on Windows set TESSERACT_PATH if needed.")
    app.run(debug=True)

