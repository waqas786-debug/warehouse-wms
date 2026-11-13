from flask import Flask, redirect, url_for
from app.extensions import db, migrate, csrf
from config import DevelopmentConfig

def create_app(config_class=DevelopmentConfig):
    flask_app = Flask(__name__)
    flask_app.config.from_object(config_class)

    db.init_app(flask_app)
    migrate.init_app(flask_app, db)
    csrf.init_app(flask_app)

    import app.models

    from app.routes.auth import auth_bp
    from app.routes.inventory import inventory_bp
    from app.routes.inbound import inbound_bp
    from app.routes.outbound import outbound_bp
    from app.routes.fleet import fleet_bp
    from app.routes.portal import portal_bp

    flask_app.register_blueprint(auth_bp, url_prefix='/auth')
    flask_app.register_blueprint(inventory_bp, url_prefix='/inventory')
    flask_app.register_blueprint(inbound_bp, url_prefix='/inbound')
    flask_app.register_blueprint(outbound_bp, url_prefix='/outbound')
    flask_app.register_blueprint(fleet_bp, url_prefix='/fleet')
    flask_app.register_blueprint(portal_bp, url_prefix='/portal')

    @flask_app.route('/')
    def root():
        return redirect(url_for('inventory.dashboard'))

    return flask_app
