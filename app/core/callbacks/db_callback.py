import resend

from app._enums import Callbacks
from app.core.callbacks.base import Callback
from app.core.config import settings
from app.models.models import CallBackExecutionResult, RoutingResponse

resend.api_key = settings.RESEND_API_KEY


class DbCallback(Callback):
    name = Callbacks.DB

    def __init__(self, *args: object, **kwargs: object) -> None:
        """
        Initialize the DbCallback.

        Args:
            *args (object): Variable length argument list.
            **kwargs (object): Arbitrary keyword arguments.

        Returns:
            None
        """

    def execute(
        self,
        **kwargs: object,
    ) -> CallBackExecutionResult:
        system_instruction: str = self._compose_system_prompt(kwargs.get("name"))

        completion_result = kwargs.get("model").generate(
            kwargs.get("content"),
            response_format=kwargs.get("response_format", RoutingResponse),
            system_instruction=system_instruction,
        )

        return CallBackExecutionResult.model_validate(
            {
                "data": {
                    "name": completion_result.data.get("name"),
                },
            }
        )
