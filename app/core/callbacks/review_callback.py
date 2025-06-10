import resend

from app._enums import Callbacks, EmailContents
from app.core.callbacks.base import Callback
from app.core.config import settings
from app.models.models import CallBackExecutionResult, FilterElement, QueryFilter
from app.services.fuzzy_match import fuzzy_find_team_member
from app.utils.sql import (
    SQLiteSQLGenerator,
)

resend.api_key = settings.resend_api_key  # type: ignore

__all__ = ["ReviewCallback"]


class ReviewCallback(Callback):
    name = Callbacks.REVIEW

    def __init__(self, *args: object, **kwargs: object) -> None:
        """
        Initialize the ReviewCallback.

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
        """
        Execute the review callback logic.

        Args:
            **kwargs (object): Arbitrary keyword arguments, expects 'username' key.

        Returns:
            CallBackExecutionResult: The result of the callback execution.
        """

        ocred_username: str = kwargs["ne"].get("Name", "") # type: ignore
        matched_user: dict = fuzzy_find_team_member(ocred_username) # type: ignore

        params: resend.Emails.SendParams = {
            "from": "Laboratory <contact@louisbrulenaudet.com>",
            "to": [matched_user.get("email", "contact@louisbrulenaudet.com"), "louisbrulenaudet@icloud.com"],
            "subject": "A new review request has been assigned to you",
            "html": EmailContents.REVIEW_REQUEST.format(
                data=kwargs.get("data", ""),
            ),
        }

        _ = resend.Emails.send(params)

        return CallBackExecutionResult.model_validate(
            {
                "data": {
                    "name": Callbacks.REVIEW,
                },
            }
        )
