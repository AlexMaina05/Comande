import pytest
from app import app as main_app # Assuming your Flask app instance is named 'app' in 'app.py'
from database import db as _db # Assuming your SQLAlchemy db instance is named 'db' in 'database.py'

@pytest.fixture(scope='session')
def app():
    """Session-wide test Flask application."""
    main_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    main_app.config['TESTING'] = True
    main_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # Other configurations can be set here

    return main_app

@pytest.fixture(scope='session')
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture(scope='session')
def db(app):
    """Session-wide test database."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()

@pytest.fixture(scope='function')
def session(db):
    """Creates a new database session for a test."""
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session_ = db.create_scoped_session(options=options)

    db.session = session_

    yield session_

    transaction.rollback()
    connection.close()
    session_.remove()
