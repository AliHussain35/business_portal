import datetime
from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user

from app.auth.decorators import role_required
from app.models import get_salary_payments, mark_salary_paid, get_employees, add_employee

bp = Blueprint("payroll", __name__, url_prefix="/payroll")


@bp.route("/")
@login_required
@role_required("owner", "accountant")
def index():
    now = datetime.date.today()
    month = request.args.get("month", now.month, type=int)
    year = request.args.get("year", now.year, type=int)
    payments = get_salary_payments(month, year)
    return render_template("payroll/index.html", payments=payments, month=month, year=year)


@bp.route("/mark-paid/<int:payment_id>", methods=["POST"])
@login_required
@role_required("owner", "accountant")
def mark_paid(payment_id):
    paid_date = request.form.get("paid_date", datetime.date.today().isoformat())
    mark_salary_paid(payment_id, paid_date)
    return redirect(url_for("payroll.index"))


@bp.route("/employees")
@login_required
@role_required("owner", "accountant")
def employees():
    return render_template("payroll/employees.html", employees=get_employees())


@bp.route("/employees/add", methods=["POST"])
@login_required
@role_required("owner", "accountant")  # both can add/edit; only Owner can delete (add that route as needed)
def add_employee_route():
    add_employee(
        name=request.form["name"],
        position=request.form.get("position"),
        monthly_salary=request.form["monthly_salary"],
        join_date=request.form.get("join_date"),
    )
    return redirect(url_for("payroll.employees"))
