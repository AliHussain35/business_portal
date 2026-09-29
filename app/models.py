from flask_login import UserMixin
from app.db import query, execute


# ---------- User ----------

class User(UserMixin):
    def __init__(self, id, name, email, role):
        self.id = id
        self.name = name
        self.email = email
        self.role = role

    @staticmethod
    def from_row(row):
        if row is None:
            return None
        return User(row["id"], row["name"], row["email"], row["role"])


def get_user_by_id(user_id):
    row = query("SELECT * FROM users WHERE id = %s", (user_id,), fetch_one=True)
    return User.from_row(row)


def get_user_by_email(email):
    row = query("SELECT * FROM users WHERE email = %s", (email,), fetch_one=True)
    return row  # raw dict, includes password_hash — used only in auth/routes.py


# ---------- Audit log ----------

def log_action(user_id, action, table_name, record_id, details=""):
    execute(
        """INSERT INTO audit_log (user_id, action, table_name, record_id, details)
           VALUES (%s, %s, %s, %s, %s)""",
        (user_id, action, table_name, record_id, details),
    )


# ---------- Employees ----------

def get_employees(include_inactive=False):
    sql = "SELECT * FROM employees WHERE is_deleted = FALSE"
    if not include_inactive:
        sql += " AND is_active = TRUE"
    sql += " ORDER BY name"
    return query(sql)


def add_employee(name, position, monthly_salary, join_date):
    return execute(
        """INSERT INTO employees (name, position, monthly_salary, join_date)
           VALUES (%s, %s, %s, %s)""",
        (name, position, monthly_salary, join_date),
    )


# ---------- Salary payments ----------

def get_salary_payments(month, year):
    return query(
        """SELECT sp.*, e.name AS employee_name
           FROM salary_payments sp
           JOIN employees e ON e.id = sp.employee_id
           WHERE sp.month = %s AND sp.year = %s AND sp.is_deleted = FALSE
           ORDER BY e.name""",
        (month, year),
    )


def mark_salary_paid(payment_id, paid_date):
    execute(
        "UPDATE salary_payments SET status = 'paid', paid_date = %s WHERE id = %s",
        (paid_date, payment_id),
    )


# ---------- Invoices ----------

def get_invoices():
    return query(
        "SELECT * FROM invoices WHERE is_deleted = FALSE ORDER BY date_received DESC"
    )


def add_invoice(vendor_name, amount, date_received, file_path, created_by):
    return execute(
        """INSERT INTO invoices (vendor_name, amount, date_received, file_path, created_by)
           VALUES (%s, %s, %s, %s, %s)""",
        (vendor_name, amount, date_received, file_path, created_by),
    )


def soft_delete_invoice(invoice_id, user_id):
    execute("UPDATE invoices SET is_deleted = TRUE WHERE id = %s", (invoice_id,))
    log_action(user_id, "delete", "invoices", invoice_id)


# ---------- Jobs (ongoing ship inspections) ----------

def get_jobs():
    return query(
        "SELECT * FROM jobs WHERE is_deleted = FALSE ORDER BY FIELD(status, 'in_progress', 'scheduled', 'completed'), updated_at DESC"
    )


def add_job(ship_name, details, status, created_by):
    return execute(
        """INSERT INTO jobs (ship_name, details, status, created_by)
           VALUES (%s, %s, %s, %s)""",
        (ship_name, details, status, created_by),
    )


def update_job_status(job_id, status):
    execute("UPDATE jobs SET status = %s WHERE id = %s", (status, job_id))


def soft_delete_job(job_id, user_id):
    execute("UPDATE jobs SET is_deleted = TRUE WHERE id = %s", (job_id,))
    log_action(user_id, "delete", "jobs", job_id)


# ---------- Attendance ----------

def has_marked_today(user_id):
    row = query(
        "SELECT * FROM attendance WHERE user_id = %s AND attendance_date = CURDATE()",
        (user_id,), fetch_one=True,
    )
    return row


def mark_attendance(user_id):
    execute(
        """INSERT INTO attendance (user_id, attendance_date)
           VALUES (%s, CURDATE())""",
        (user_id,),
    )


def get_attendance_records(date=None):
    if date:
        return query(
            """SELECT a.*, u.name AS user_name
               FROM attendance a JOIN users u ON u.id = a.user_id
               WHERE a.attendance_date = %s
               ORDER BY a.marked_at""",
            (date,),
        )
    return query(
        """SELECT a.*, u.name AS user_name
           FROM attendance a JOIN users u ON u.id = a.user_id
           ORDER BY a.attendance_date DESC, a.marked_at DESC
           LIMIT 200"""
    )


# ---------- Login history ----------

def log_login(user_id, ip_address, city, country):
    execute(
        """INSERT INTO login_history (user_id, ip_address, city, country)
           VALUES (%s, %s, %s, %s)""",
        (user_id, ip_address, city, country),
    )


def get_login_history(limit=100):
    return query(
        """SELECT lh.*, u.name AS user_name
           FROM login_history lh
           JOIN users u ON u.id = lh.user_id
           ORDER BY lh.logged_in_at DESC
           LIMIT %s""",
        (limit,),
    )


# ---------- Cash transactions ----------

def get_cash_transactions():
    return query(
        "SELECT * FROM cash_transactions WHERE is_deleted = FALSE ORDER BY date DESC"
    )


def add_cash_transaction(type_, amount, category, date, description, created_by):
    return execute(
        """INSERT INTO cash_transactions (type, amount, category, date, description, created_by)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (type_, amount, category, date, description, created_by),
    )


def soft_delete_cash_transaction(transaction_id, user_id):
    execute("UPDATE cash_transactions SET is_deleted = TRUE WHERE id = %s", (transaction_id,))
    log_action(user_id, "delete", "cash_transactions", transaction_id)


def get_cash_balance():
    row = query(
        """SELECT
             COALESCE(SUM(CASE WHEN type = 'in' THEN amount ELSE 0 END), 0) -
             COALESCE(SUM(CASE WHEN type = 'out' THEN amount ELSE 0 END), 0) AS balance
           FROM cash_transactions WHERE is_deleted = FALSE""",
        fetch_one=True,
    )
    return row["balance"]
