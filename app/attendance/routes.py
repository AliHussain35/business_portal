import datetime
from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user

from app.auth.decorators import role_required
from app.models import has_marked_today, mark_attendance, get_attendance_records

bp = Blueprint("attendance", __name__, url_prefix="/attendance")


@bp.route("/")
@login_required
@role_required("employee")
def mark():
    """Employee's own attendance page - mark arrival for today."""
    today_entry = has_marked_today(current_user.id)
    return render_template("attendance/mark.html", today_entry=today_entry)


@bp.route("/mark", methods=["POST"])
@login_required
@role_required("employee")
def do_mark():
    if not has_marked_today(current_user.id):
        mark_attendance(current_user.id)
    return redirect(url_for("attendance.mark"))


@bp.route("/records")
@login_required
@role_required("owner", "accountant")
def records():
    """Owner/accountant view of everyone's attendance."""
    date_filter = request.args.get("date")
    entries = get_attendance_records(date_filter)
    return render_template("attendance/records.html", entries=entries, date_filter=date_filter)
