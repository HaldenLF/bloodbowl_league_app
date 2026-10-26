import itertools
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import Base, get_db
from app.core.security import create_access_token, hash_password
from app.main import app
from app.models.users import AccountType, User

TEST_PASSWORD = "my-lovely-horse"
_numbers = itertools.count(1)


@pytest.fixture(scope="session")
def engine():
    url = settings.test_database_url
    if url is None or not make_url(url).database.endswith("_test"):
        pytest.exit("TEST_DATABASE_URL must be set and name a database ending in _test", returncode=1)
    engine = create_engine(url)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def db(engine):
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db):
    app.dependency_overrides[get_db] = lambda: db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def password_hash():
    return hash_password(TEST_PASSWORD)


@pytest.fixture
def make_user(db, password_hash):
    def make(account_type: AccountType = AccountType.COACH, is_active: bool = True) -> User:
        number = next(_numbers)
        user = User(
            email=f"user{number}@example.com",
            display_name=f"User {number}",
            password_hash=password_hash,
            account_type=account_type,
            is_active=is_active,
        )
        db.add(user)
        db.flush()
        return user
    return make


@pytest.fixture
def coach(make_user):
    return make_user(AccountType.COACH)


@pytest.fixture
def commissioner(make_user):
    return make_user(AccountType.COMMISSIONER)


@pytest.fixture
def super_admin(make_user):
    return make_user(AccountType.SUPER_ADMIN)


@pytest.fixture
def auth():
    def headers(user: User) -> dict[str, str]:
        return {"Authorization": f"Bearer {create_access_token(user.id)}"}
    return headers


@pytest.fixture
def make_league(client, auth):
    def make(owner: User, join_policy: str = "invite_only") -> dict:
        response = client.post(
            "/leagues",
            json={"name": f"League {next(_numbers)}", "join_policy": join_policy},
            headers=auth(owner),
        )
        assert response.status_code == 201, response.text
        return response.json()
    return make


@pytest.fixture
def add_member(client, auth):
    def add(user: User, league: dict) -> None:
        response = client.post("/leagues/join", json={"join_code": league["join_code"]}, headers=auth(user))
        assert response.status_code == 200, response.text
    return add


@pytest.fixture
def make_season(client, auth):
    def make(owner: User, league: dict, starting_treasury: int = 1_000_000) -> dict:
        response = client.post(
            f"/leagues/{league['id']}/seasons",
            json={"name": f"Season {next(_numbers)}", "format": "16s", "starting_treasury": starting_treasury},
            headers=auth(owner),
        )
        assert response.status_code == 201, response.text
        return response.json()
    return make
