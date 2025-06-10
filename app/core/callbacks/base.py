from __future__ import annotations

from typing import Protocol

from app._enums import Callback as CallbackEnum


class Callback(Protocol):
    """
    Protocol defining the interface for a callback.

    A callback must implement an async `execute` method that performs its action
    and returns a AgentExecutionResult. Each callback must have a `name` attribute from the Callbacks enum.
    """

    name: CallbackEnum

    def __init__(self, *args: object, **kwargs: object) -> None: ...
