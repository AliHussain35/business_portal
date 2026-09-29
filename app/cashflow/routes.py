from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user

from app.auth.decorators import role_required
from app.models import (
    get_cash_transactions,
    add_cash_transaction,
    soft_delete_cash_transaction,
    get_cash_balance,
)

bp = Blueprint("cashflow", __name__, url_prefix="/cashflow")


@bp.route("/")
@login_required
@role_required("owner", "accountant")
def index():
    transactions = get_cash_transactions()
    balance = get_cash_balance()
    return render_template("cashflow/index.html", transactions=transactions, balance=balance)


@bp.route("/add", methods=["POST"])
@login_required
@role_required("owner", "accountant")
def add():
    add_cash_transaction(
        type_=request.form["type"],
        amount=request.form["amount"],
        category=request.form.get("category"),
        date=request.form["date"],
        description=request.form.get("description"),
        created_by=current_user.id,
    )
    return redirect(url_for("cashflow.index"))


@bp.route("/delete/<int:transaction_id>", methods=["POST"])
@login_required
@role_required("owner", "accountant")
def delete(transaction_id):
    soft_delete_cash_transaction(transaction_id, current_user.id)
    return redirect(url_for("cashflow.index"))
