import logging
from datetime import datetime, timedelta

from fastapi import Request, HTTPException
import jwt


JWT_SECRET_KEY = (
    "canonical_audit_log_service"  # todo add to service config : ENV variable
)
JWT_ALGORITHM = "HS256"  # todo add to service config : ENV variable
AllOWED_ACCESS_KEY = (
    "canonical_audit_log_service_all_access"  # todo add to service config: ENV variable
)

logger = logging.getLogger(__name__)


class AuthController:
    """
    AuthController provides authentication services for the audit log service,
    including validating and generating JWT tokens for access control.

    Attributes:
        None

    Methods:
        validate_access_token(request: Request): Validates the JWT access token from the request's authorization header.
        generate_access_token(valid_minutes: int): Generates a new JWT access token with a specified validity period.
    """

    @staticmethod
    def validate_access_token(request: Request) -> None:
        """
        Validates the JWT access token provided in the 'Authorization' header of the request.

        Parameters:
            request (Request): The FastAPI request object containing the HTTP request details.

        Returns:
            None. The method returns early if the token is valid.

        Raises:
            HTTPException: 401 error if the token is missing, expired, or invalid.
            HTTPException: 500 error if any other exception occurs during validation.
        """
        auth_header = request.headers.get("authorization")
        if not auth_header:
            raise HTTPException(status_code=401, detail="Access token is missing.")
        try:
            token = auth_header.split(" ")[1]
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            if payload.get("key") != AllOWED_ACCESS_KEY:
                raise jwt.InvalidTokenError()
        except jwt.ExpiredSignatureError:
            logger.debug("Access token is expired.")
            raise HTTPException(status_code=401, detail="Token expired.")
        except jwt.InvalidTokenError:
            logger.debug("Access token is invalid.")
            raise HTTPException(status_code=401, detail="Invalid token.")
        except Exception as e:
            logger.error(f"Error while validating token: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500, detail="Something went wrong, please try again."
            )

    @staticmethod
    def generate_access_token(valid_minutes: int) -> dict:
        """
        Generates a new JWT access token with a specified validity period in minutes.

        Parameters:
            valid_minutes (int): The number of minutes for which the token will be valid.

        Returns:
            dict: A dictionary containing the generated token.

        Raises:
            HTTPException: 500 error if any exception occurs during token generation.
        """
        try:
            expiration = datetime.utcnow() + timedelta(minutes=valid_minutes)
            token = jwt.encode(
                {"key": AllOWED_ACCESS_KEY, "exp": expiration},
                JWT_SECRET_KEY,
                algorithm=JWT_ALGORITHM,
            )
            return {"token": token}
        except Exception as e:
            logger.error(f"Error while generating token: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500, detail="Something went wrong, please try again."
            )
