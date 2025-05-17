from app.models.user import User
from app.extensions import db

def test_create_user(client, app):
    # tạo đối tượng User mới
    u = User(
        username="alice",
        full_name="Alice Example",
        email="alice@example.com",
        password_hash="hash"
    )
    db.session.add(u)
    db.session.commit()

    # kiểm tra query
    users = User.query.all()
    assert len(users) == 1
    assert users[0].username == "alice"
