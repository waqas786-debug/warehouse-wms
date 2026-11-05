import pytest
from app import create_app
from app.extensions import db
from config import TestingConfig
from app.models.auth import Role, User
from werkzeug.security import generate_password_hash

@pytest.fixture
def app():
    app = create_app(TestingConfig)
    with app.app_context():
        db.create_all()
        role = Role(name='Administrator', description='Admin role')
        db.session.add(role)
        db.session.flush()

        user = User(
            username='testadmin',
            email='test@wms.local',
            password_hash=generate_password_hash('testpass123'),
            role_id=role.id,
            is_active=True
        )
        db.session.add(user)
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_client(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['username'] = 'testadmin'
        sess['role'] = 'Administrator'
    return client
