import pytest
from fastapi import HTTPException
from datetime import datetime, timedelta
import jwt

from log_service.controllers.auth_controller import (
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
    AuthController,
    AllOWED_ACCESS_KEY,
)


# Utility function to generate tokens for tests
def generate_jwt(payload):
    return (
        jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM).decode("utf-8")
        if hasattr(
            jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM), "decode"
        )
        else jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    )


@pytest.fixture
def mock_request(mocker):
    return mocker.MagicMock()


# Test cases


def test_validate_access_token_missing(mocker, mock_request):
    mock_request.headers.get.return_value = None
    with pytest.raises(HTTPException) as exc:
        AuthController.validate_access_token(mock_request)
    assert exc.value.status_code == 401
    assert exc.value.detail == "Access token is missing."


def test_validate_access_token_valid(mocker, mock_request):
    valid_payload = {
        "key": AllOWED_ACCESS_KEY,
        "exp": datetime.utcnow() + timedelta(minutes=5),
    }
    token = generate_jwt(valid_payload)
    mock_request.headers.get.return_value = f"Bearer {token}"
    # Test should pass without exceptions
    AuthController.validate_access_token(mock_request)


def test_validate_access_token_wrong_token(mocker, mock_request):
    valid_payload = {
        "key": AllOWED_ACCESS_KEY + "invalid",
        "exp": datetime.utcnow() + timedelta(minutes=5),
    }
    token = generate_jwt(valid_payload)
    mock_request.headers.get.return_value = f"Bearer {token}"
    with pytest.raises(HTTPException) as exc:
        AuthController.validate_access_token(mock_request)
    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid token."


def test_validate_access_token_expired(mocker, mock_request):
    expired_payload = {
        "key": AllOWED_ACCESS_KEY,
        "exp": datetime.utcnow() - timedelta(minutes=1),
    }
    token = generate_jwt(expired_payload)
    mock_request.headers.get.return_value = f"Bearer {token}"
    with pytest.raises(HTTPException) as exc:
        AuthController.validate_access_token(mock_request)
    assert exc.value.status_code == 401
    assert exc.value.detail == "Token expired."


def test_validate_access_token_invalid(mocker, mock_request):
    mocker.patch("jwt.decode", side_effect=jwt.InvalidTokenError)
    mock_request.headers.get.return_value = "Bearer invalidtoken"
    with pytest.raises(HTTPException) as exc:
        AuthController.validate_access_token(mock_request)
    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid token."


def test_validate_token_unhandled_exception(mocker, mock_request):
    mocker.patch("jwt.decode", side_effect=ValueError)
    mock_request.headers.get.return_value = "Bearer invalidtoken"
    with pytest.raises(HTTPException) as exc:
        AuthController.validate_access_token(mock_request)
    assert exc.value.status_code == 500
    assert exc.value.detail == "Something went wrong, please try again."


def test_generate_access_token(mocker):
    valid_minutes = 5
    token_info = AuthController.generate_access_token(valid_minutes)
    assert "token" in token_info
    # Decode the token without verification for testing purpose
    decoded = jwt.decode(
        token_info["token"],
        JWT_SECRET_KEY,
        algorithms=[JWT_ALGORITHM],
        options={"verify_signature": False},
    )
    assert decoded["key"] == AllOWED_ACCESS_KEY
    # More detailed assertions can be added to verify the expiration logic


def test_generate_access_token_unhandled_exception(mocker):
    valid_minutes = 5
    mocker.patch("jwt.encode", side_effect=ValueError)
    with pytest.raises(HTTPException) as exc:
        AuthController.generate_access_token(valid_minutes)
    assert exc.value.status_code == 500
    assert exc.value.detail == "Something went wrong, please try again."
