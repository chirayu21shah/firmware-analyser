from flask import Flask

from app.services.job_manager import JobManager
from .routes.health import health_check
from .routes.analyse import analyse_bp

def register_routes(app):
    app.register_blueprint(health_check)
    app.register_blueprint(analyse_bp)

def create_app():
    app = Flask(__name__)
    app.extensions['job_manager'] = JobManager()
    register_routes(app)

    return app