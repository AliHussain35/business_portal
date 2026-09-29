from flask import Flask
from flask_login import LoginManager

from config import Config
from app import db as db_module
from app.models import get_user_by_id

login_manager = LoginManager()
login_manager.login_view = "auth.login"


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db_module.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return get_user_by_id(user_id)

    from app.auth.routes import bp as auth_bp
    from app.dashboard.routes import bp as dashboard_bp
    from app.payroll.routes import bp as payroll_bp
    from app.invoices.routes import bp as invoices_bp
    from app.cashflow.routes import bp as cashflow_bp
    from app.attendance.routes import bp as attendance_bp
    from app.jobs.routes import bp as jobs_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(payroll_bp)
    app.register_blueprint(invoices_bp)
    app.register_blueprint(cashflow_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(jobs_bp)

    return app
