from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user

from app.auth.decorators import role_required
from app.models import get_jobs, add_job, update_job_status, soft_delete_job

bp = Blueprint("jobs", __name__, url_prefix="/jobs")


@bp.route("/")
@login_required
@role_required("owner", "accountant", "employee")
def index():
    """Everyone can view; template hides add/edit controls for employees."""
    jobs = get_jobs()
    return render_template("jobs/index.html", jobs=jobs)


@bp.route("/add", methods=["POST"])
@login_required
@role_required("owner", "accountant")
def add():
    add_job(
        ship_name=request.form["ship_name"],
        details=request.form.get("details"),
        status=request.form.get("status", "scheduled"),
        created_by=current_user.id,
    )
    return redirect(url_for("jobs.index"))


@bp.route("/update-status/<int:job_id>", methods=["POST"])
@login_required
@role_required("owner", "accountant")
def update_status(job_id):
    update_job_status(job_id, request.form["status"])
    return redirect(url_for("jobs.index"))


@bp.route("/delete/<int:job_id>", methods=["POST"])
@login_required
@role_required("owner", "accountant")
def delete(job_id):
    soft_delete_job(job_id, current_user.id)
    return redirect(url_for("jobs.index"))
