# Copyright (C) 2022-2023 Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE, Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

from abc import ABCMeta
from abc import abstractmethod
from http.client import BAD_REQUEST
from http.client import CONFLICT
from http.client import INTERNAL_SERVER_ERROR
from http.client import NOT_FOUND
from http.client import SERVICE_UNAVAILABLE
from http.client import UNAUTHORIZED
from http.client import UNPROCESSABLE_ENTITY
from typing import Sequence

from pydantic.error_wrappers import ErrorList


class ServiceException(Exception, metaclass=ABCMeta):
    """Base class for service exceptions."""

    domain: str = 'global'

    @property
    @abstractmethod
    def status(self) -> int:
        """HTTP status code applicable to the problem."""

        raise NotImplementedError

    @property
    @abstractmethod
    def code(self) -> str:
        """Component-specific error code."""

        raise NotImplementedError

    @property
    @abstractmethod
    def details(self) -> str:
        """Additional information with specific explanation for this occurrence of the problem."""

        raise NotImplementedError

    def dict(self) -> dict[str, str]:
        """Represent error as dictionary."""

        return {
            'code': f'{self.domain}.{self.code}',
            'details': self.details,
        }


class ServiceNotAvailable(ServiceException):
    """Raised when external service is not available."""

    @property
    def status(self) -> int:
        return SERVICE_UNAVAILABLE

    @property
    def code(self) -> str:
        return 'service_unavailable'

    @property
    def details(self) -> str:
        return 'Requested external service is not available'


class UnhandledException(ServiceException):
    """Raised when unhandled/unexpected internal error occurred."""

    @property
    def status(self) -> int:
        return INTERNAL_SERVER_ERROR

    @property
    def code(self) -> str:
        return 'unhandled_exception'

    @property
    def details(self) -> str:
        return 'Unexpected Internal Server Error'


class NotFound(ServiceException):
    """Raised when requested resource is not found."""

    @property
    def status(self) -> int:
        return NOT_FOUND

    @property
    def code(self) -> str:
        return 'not_found'

    @property
    def details(self) -> str:
        return 'Requested resource is not found'


class AlreadyExists(ServiceException):
    """Raised when target resource already exists."""

    @property
    def status(self) -> int:
        return CONFLICT

    @property
    def code(self) -> str:
        return 'already_exists'

    @property
    def details(self) -> str:
        return 'Target resource already exists'


class InvalidInput(ServiceException):
    """Raised when target resource is invalid."""

    @property
    def status(self) -> int:
        return BAD_REQUEST

    @property
    def code(self) -> str:
        return 'invalid_input'

    @property
    def details(self) -> str:
        return 'Invalid input resource'


class BadRequest(ServiceException):
    """Raised when client error exists for a target resource."""

    @property
    def status(self) -> int:
        return BAD_REQUEST

    @property
    def code(self) -> str:
        return 'bad_request'

    @property
    def details(self) -> str:
        return 'Target resource cannot be processed'


class ServiceValidationError(ServiceException):
    """Raised when validation error is raised."""

    def __init__(self, errors: Sequence[ErrorList], *args, **kwargs) -> None:
        self.errors = errors

    @property
    def status(self) -> int:
        return UNPROCESSABLE_ENTITY

    @property
    def code(self) -> str:
        return 'validation_error'

    def dict(self) -> dict[str, str]:
        """Represent error as dictionary."""
        errors = []
        for error in self.errors:
            errors.append(
                {
                    'code': self.code,
                    'detail': error.get('msg'),
                    'source': error.get('loc'),
                }
            )

        return errors


class Unauthorized(ServiceException):
    """Raised when user authentication fails for a given resource."""

    @property
    def status(self) -> int:
        return UNAUTHORIZED

    @property
    def code(self) -> str:
        return 'unauthorized'

    @property
    def details(self) -> str:
        return 'User authentication error'
