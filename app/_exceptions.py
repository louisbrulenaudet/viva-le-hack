from __future__ import annotations

from typing import Any

from app._enums import ErrorCodes
from app.utils.logger import logger

__all__ = [
    "CoreError",
    "CompletionError",
    "AgentRegistryNotFoundError",
    "AgentInitializationError",
    "AgentExecutionError",
    "AgentConfigurationError",
    "SystemPromptError",
]


class CoreError(Exception):
    """
    A custom exception class for handling application-specific errors.

    This exception includes an error message, an error code, and optional details.
    It also logs the error upon initialization.

    Attributes:
        message (str): A descriptive error message.
        code (ErrorCodes): An enumerated error code representing the specific error type.
        details (dict[str, Any] | str | None): Additional details about the error.
    """

    message: str
    code: ErrorCodes
    details: dict[str, Any] | str | None

    def __init__(
        self,
        message: str,
        code: ErrorCodes,
        details: dict[str, Any] | str | None = None,
    ) -> None:
        """
        Initialize a CoreError instance with an error message, code, and optional details.

        The error is logged automatically when an instance is created.

        Args:
            message (str): The error message.
            code (ErrorCodes): A predefined error code representing the error type.
            details (dict[str, Any] | str | None, optional): Additional information about the error.
                Can be a dictionary, a string, or None. Defaults to None.
        """
        self.message = message
        self.code = code
        self.details = details

        logger.error(
            f"{self.__class__.__name__}: {message} [Code: {code}] Details: {details}"
        )

    def __str__(self) -> str:
        """
        Return a string representation of the error, including the message, code, and optional details.

        Returns:
            str: A formatted string describing the error.

        Example:
            >>> error = CoreError("Invalid input", ErrorCodes.INVALID_INPUT, {"field": "email"})
            >>> print(str(error))
            "CoreError: Invalid input [Code: INVALID_INPUT] Details: {'field': 'email'}"
        """
        detail_part = f" Details: {self.details}" if self.details else ""
        return f"{self.__class__.__name__}: {self.message} [Code: {self.code}]{detail_part}"

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the CoreError instance into a dictionary format.

        This is useful for structured logging or returning errors in API responses.

        Returns:
            dict[str, Any]: A dictionary containing error details.

        Example:
            >>> error = CoreError("Access denied", ErrorCodes.PERMISSION_DENIED, "User lacks admin rights")
            >>> error.to_dict()
            {
                "error": "CoreError",
                "message": "Access denied",
                "code": "PERMISSION_DENIED",
                "details": "User lacks admin rights"
            }
        """
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "code": self.code,
            "details": self.details or {},
        }


class CompletionError(CoreError):
    def __init__(self, details: Exception | str) -> None:
        super().__init__(
            "The completion failed to produce a result.",
            ErrorCodes.COMPLETION_ERROR,
            details=str(details),
        )


class ClientInitializationError(CoreError):
    def __init__(self, details: Exception | str) -> None:
        super().__init__(
            "The client initialization failed.",
            ErrorCodes.CLIENT_INITIALIZATION_ERROR,
            details=str(details),
        )


class AgentRegistryNotFoundError(CoreError):  # Renamed from ToolRegistryNotFoundError
    def __init__(self) -> None:
        super().__init__(
            "The agent registry was not found.",
            ErrorCodes.TOOL_REGISTRY_NOT_FOUND,  # TODO: Consider new ErrorCode: AGENT_REGISTRY_NOT_FOUND
            "This error occurs when the agent registry is not available or has not been initialized.",
        )


class AgentInitializationError(CoreError):  # Renamed from ToolInitializationError
    def __init__(self, details: Exception | str) -> None:
        super().__init__(
            "The agent initialization failed.",
            ErrorCodes.TOOL_INITIALIZATION_ERROR,  # TODO: Consider new ErrorCode: AGENT_INITIALIZATION_ERROR
            details=str(details),
        )


class AgentExecutionError(CoreError):  # Renamed from ToolExecutionError
    def __init__(self, details: Exception | str) -> None:
        super().__init__(
            "The agent execution failed.",
            ErrorCodes.TOOL_EXECUTION_ERROR,  # TODO: Consider new ErrorCode: AGENT_EXECUTION_ERROR
            details=str(details),
        )


class AgentConfigurationError(CoreError):  # Renamed from ToolConfigurationError
    def __init__(self, details: Exception | str) -> None:
        super().__init__(
            "The agent configuration failed.",
            ErrorCodes.TOOL_CONFIGURATION_ERROR,  # TODO: Consider new ErrorCode: AGENT_CONFIGURATION_ERROR
            details=str(details),
        )


class SystemPromptError(CoreError):
    def __init__(self, details: Exception | str) -> None:
        super().__init__(
            "System prompt initialization failed.",
            ErrorCodes.SYSTEM_PROMPT_ERROR,
            details=str(details),
        )


class MCPDatabaseInitializationError(CoreError):
    def __init__(self, details: Exception | str) -> None:
        super().__init__(
            "The MCP database initialization failed.",
            ErrorCodes.MCP_DATABASE_INITIALIZATION_ERROR,
            details=str(details),
        )
