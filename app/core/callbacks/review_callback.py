import resend

from app._enums import Callbacks, EmailContents
from app.core.callbacks.base import Callback
from app.core.config import settings
from app.models.models import CallBackExecutionResult, FilterElement, QueryFilter
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
        user = (
            settings.cloudflare_client.d1.database.query(
                database_id=settings.cloudflare_db_id,
                account_id=settings.cloudflare_account_id,
                sql=SQLiteSQLGenerator.compile(
                    QueryFilter(
                        base_table="team",
                        fields=["email"],
                        filters=[
                            FilterElement(
                                field="username",
                                operator="=",
                                value=kwargs.get("username", ""),
                            ),
                        ],
                        limit=1,
                    )
                ),
            )
            .result[0]
            .results
        )

        params: resend.Emails.SendParams = {
            "from": "Laboratory <contact@louisbrulenaudet.com>",
            "to": [user[0].get("email", "contact@louisbrulenaudet.com"), "louisbrulenaudet@icloud.com"],
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
