from datetime import timedelta

from app.infrastructure.auth.jwt_handler import JWTHandler


def test_password_hash_and_verify():
    password = "super-secret-password"
    hashed = JWTHandler.hash_password(password)

    assert hashed != password
    assert JWTHandler.verify_password(password, hashed) is True
    assert JWTHandler.verify_password("wrong", hashed) is False


def test_create_and_decode_jwt_token_roundtrip():
    token = JWTHandler.create_access_token(
        data={"sub": "user@example.com", "role": "user"},
        expires_delta=timedelta(minutes=5),
    )
    payload = JWTHandler.decode_token(token)

    assert payload["sub"] == "user@example.com"
    assert payload["role"] == "user"
    assert "exp" in payload
