import datetime
from flask import Blueprint, render_template
from flask_login import login_required

from app.auth.decorators import role_required
from app.models import get_cash_balance, get_salary_payments, get_invoices, get_login_history

bp = Blueprint("dashboard", __name__, url_prefix="/")


@bp.route("/login-history")
@login_required
@role_required("owner")
def login_history():
    return render_template("dashboard/login_history.html", entries=get_login_history())


@bp.route("/")
@login_required
@role_required("owner", "accountant")
def index():
    now = datetime.date.today()
    balance = get_cash_balance()
    salaries_this_month = get_salary_payments(now.month, now.year)
    unpaid_count = sum(1 for p in salaries_this_month if p["status"] == "unpaid")
    pending_invoices = [i for i in get_invoices() if i["status"] == "pending"]

    return render_template(
        "dashboard/index.html",
        balance=balance,
        unpaid_salaries=unpaid_count,
        pending_invoices=len(pending_invoices),
    )
