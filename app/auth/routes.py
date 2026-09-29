from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash

from app.models import get_user_by_email, get_user_by_id, User, log_login
from app.geo import get_client_ip, resolve_location

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        row = get_user_by_email(email)
        if row and check_password_hash(row["password_hash"], password):
            login_user(User.from_row(row))

            ip = get_client_ip(request)
            city, country = resolve_location(ip)
            log_login(row["id"], ip, city, country)

            if row["role"] == "employee":
                return redirect(url_for("attendance.mark"))
            return redirect(url_for("dashboard.index"))

        flash("Invalid email or password", "error")

    return render_template("login.html")


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
