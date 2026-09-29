from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user

from app.auth.decorators import role_required
from app.models import get_invoices, add_invoice, soft_delete_invoice

bp = Blueprint("invoices", __name__, url_prefix="/invoices")


@bp.route("/")
@login_required
@role_required("owner", "accountant")
def index():
    invoices = get_invoices()
    return render_template("invoices/index.html", invoices=invoices)


@bp.route("/add", methods=["POST"])
@login_required
@role_required("owner", "accountant")
def add():
    # File upload handling (saving to disk / cloud storage) can be added here;
    # for now we assume a file_path is passed in or left blank.
    add_invoice(
        vendor_name=request.form["vendor_name"],
        amount=request.form["amount"],
        date_received=request.form["date_received"],
        file_path=request.form.get("file_path"),
        created_by=current_user.id,
    )
    return redirect(url_for("invoices.index"))


@bp.route("/delete/<int:invoice_id>", methods=["POST"])
@login_required
@role_required("owner", "accountant")
def delete(invoice_id):
    soft_delete_invoice(invoice_id, current_user.id)
    return redirect(url_for("invoices.index"))
