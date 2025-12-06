import os
import csv
from io import StringIO
from flask import Flask, render_template, redirect, url_for, request, flash, make_response
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from jinja2 import TemplateNotFound
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from models import db, User, Trip, Activity
from datetime import datetime

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(Config)

    # Initialize database
    db.init_app(app)
    
    # Initialize login manager
    login_manager = LoginManager()
    login_manager.login_view = "login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return User.query.get(int(user_id))
        except Exception:
            return None

    # ------------------------------
    # Initialization code
    # This replaces before_first_request
    # ------------------------------
    with app.app_context():
        os.makedirs(os.path.join(os.path.dirname(__file__), "database"), exist_ok=True)
        db.create_all()

    # Optional: Run code on first request using a flag
    first_request_done = {'done': False}

    @app.before_request
    def run_once_before_first_request():
        if not first_request_done['done']:
            # Put any code you want to run once here
            print("Running first-request initialization...")
            first_request_done['done'] = True

    # ------------------------------
    # Routes
    # ------------------------------
    @app.route("/")
    def index():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))
        return render_template("index.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                login_user(user)
                return redirect(url_for("dashboard"))
            flash("Invalid credentials", "danger")
        try:
            return render_template("login.html")
        except TemplateNotFound:
            return redirect(url_for("index"))

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            username = request.form.get("username")
            email = request.form.get("email")
            password = request.form.get("password")
            if User.query.filter_by(username=username).first():
                flash("Username exists", "warning")
                return redirect(url_for("register"))
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash("Account created. Please log in.", "success")
            return redirect(url_for("login"))
        try:
            return render_template("register.html")
        except TemplateNotFound:
            return redirect(url_for("index"))

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        flash("Logged out.", "info")
        return redirect(url_for("index"))

    @app.route("/dashboard")
    @login_required
    def dashboard():
        trips = Trip.query.filter_by(user_id=current_user.id, deleted=False).all()
        stats = {"upcoming": 0, "next_trip": "—", "completed": 0, "saved_places": 0, "budget": 0}
        recent_notes = []
        return render_template("dashboard.html", trips=trips, stats=stats, recent_notes=recent_notes)

    @app.route("/trip/new", methods=["GET", "POST"])
    @login_required
    def new_trip():
        if request.method == "POST":
            try:
                start_date = datetime.strptime(request.form.get("start_date"), "%Y-%m-%d").date() if request.form.get("start_date") else None
                end_date = datetime.strptime(request.form.get("end_date"), "%Y-%m-%d").date() if request.form.get("end_date") else None
                
                trip = Trip(
                    user_id=current_user.id,
                    title=request.form.get("title") or None,
                    destination=request.form.get("destination"),
                    start_date=start_date,
                    end_date=end_date,
                    travelers=int(request.form.get("travelers", 1)),
                    budget_preference=request.form.get("budget_preference", "medium")
                )
                db.session.add(trip)
                db.session.commit()
                flash("Trip created.", "success")
                return redirect(url_for("dashboard"))
            except Exception as e:
                flash(f"Error creating trip: {str(e)}", "danger")
                return redirect(url_for("new_trip"))
        return render_template("new_trip.html")

    @app.route("/trip/<int:trip_id>")
    @login_required
    def view_trip(trip_id):
        trip = Trip.query.filter_by(id=trip_id, user_id=current_user.id, deleted=False).first()
        if not trip:
            flash("Trip not found or access denied.", "warning")
            return redirect(url_for("dashboard"))
        return render_template("view_trip.html", trip=trip)

    @app.route("/trip/<int:trip_id>/edit", methods=["GET", "POST"])
    @login_required
    def edit_trip(trip_id):
        trip = Trip.query.filter_by(id=trip_id, user_id=current_user.id).first()
        if not trip:
            flash("Trip not found or access denied.", "warning")
            return redirect(url_for("dashboard"))

        if request.method == "POST":
            try:
                trip.title = request.form.get("title") or None
                trip.destination = request.form.get("destination") or trip.destination
                sd = request.form.get("start_date")
                ed = request.form.get("end_date")
                trip.start_date = datetime.strptime(sd, "%Y-%m-%d").date() if sd else None
                trip.end_date = datetime.strptime(ed, "%Y-%m-%d").date() if ed else None
                trip.travelers = int(request.form.get("travelers", trip.travelers or 1))
                trip.budget_preference = request.form.get("budget_preference", trip.budget_preference or "medium")
                total_budget = request.form.get("total_budget")
                trip.total_budget = float(total_budget) if total_budget not in (None, "") else (trip.total_budget or 0.0)
                trip.summary = request.form.get("summary") or None

                db.session.commit()
                flash("Trip updated.", "success")
                return redirect(url_for("view_trip", trip_id=trip.id))
            except Exception as e:
                db.session.rollback()
                flash(f"Error updating trip: {e}", "danger")

        return render_template("edit_trip.html", trip=trip)

    @app.route("/admin")
    @login_required
    def admin_index():
        if not current_user.is_admin:
            flash("Admin access required.", "danger")
            return redirect(url_for("index"))
        users = User.query.all()
        trips = Trip.query.filter_by(deleted=False).limit(50).all()
        return render_template("admin/dashboard.html", users=users, trips=trips)

    @app.route("/admin/export")
    @login_required
    def admin_export_all():
        if not current_user.is_admin:
            flash("Admin access required.", "danger")
            return redirect(url_for("index"))
        trips = Trip.query.filter_by(deleted=False).all()
        si = StringIO()
        w = csv.writer(si)
        w.writerow(["user_id", "title", "destination", "start_date", "end_date", "status"])
        for t in trips:
            title = (getattr(t, "title", None) or "").strip()
            w.writerow([
                t.user_id,
                title,
                getattr(t, "destination", ""),
                t.start_date.strftime("%Y-%m-%d") if t.start_date else "",
                t.end_date.strftime("%Y-%m-%d") if t.end_date else "",
                getattr(t, "status", "")
            ])
        out = make_response(si.getvalue())
        out.headers["Content-Disposition"] = "attachment; filename=all_trips.csv"
        out.headers["Content-Type"] = "text/csv; charset=utf-8"
        return out

    @app.route("/admin/users")
    @login_required
    def admin_users():
        if not current_user.is_admin:
            flash("Admin access required.", "danger")
            return redirect(url_for("index"))
        users = User.query.all()
        return render_template("admin/users.html", users=users)

    @app.route("/profile")
    @login_required
    def profile():
        return render_template("profile.html")

    @app.route("/settings")
    @login_required
    def settings():
        return render_template("settings.html")

    @app.route("/import", methods=["GET", "POST"])
    @login_required
    def import_trips():
        if request.method == "POST":
            flash("Import completed (placeholder).", "success")
            return redirect(url_for("dashboard"))
        return render_template("import_trips.html")

    @app.route("/export")
    @login_required
    def export_data():
        trips = Trip.query.filter_by(user_id=current_user.id, deleted=False).all()
        si = StringIO()
        w = csv.writer(si)
        w.writerow(["title", "destination", "start_date", "end_date", "status"])
        def fmt(d):
            if d is None: return ""
            if hasattr(d, "strftime"): return d.strftime("%Y-%m-%d")
            return str(d)
        for t in trips:
            title = (getattr(t, "title", None) or getattr(t, "destination", "") or "").strip()
            w.writerow([title, getattr(t, "destination", ""), fmt(getattr(t, "start_date", None)), fmt(getattr(t, "end_date", None)), getattr(t, "status", "")])
        out = make_response(si.getvalue())
        out.headers["Content-Disposition"] = "attachment; filename=trips.csv"
        out.headers["Content-Type"] = "text/csv; charset=utf-8"
        return out

    @app.route("/trip/<int:trip_id>/delete", methods=["POST"])
    @login_required
    def delete_trip(trip_id):
        trip = Trip.query.filter_by(id=trip_id, user_id=current_user.id).first()
        if not trip:
            flash("Trip not found or access denied.", "warning")
            return redirect(url_for("dashboard"))
        try:
            trip.deleted = True
            trip.deleted_at = datetime.utcnow()
            db.session.commit()
            flash("Trip moved to Trash (soft-deleted).", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error deleting trip: {e}", "danger")
        return redirect(url_for("dashboard"))

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
