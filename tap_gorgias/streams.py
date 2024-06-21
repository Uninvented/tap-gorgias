"""Stream type classes for tap-gorgias."""
from urllib import parse
from datetime import datetime
import logging
import json
import requests
from typing import Any, Dict, Optional, Iterable, cast
from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_gorgias.client import GorgiasStream

logger = logging.getLogger(__name__)

CUSTOMER_SCHEMA = [
    th.ObjectType(
        th.Property("id", th.IntegerType),
        th.Property("email", th.StringType),
        th.Property("name", th.StringType),
        th.Property("firstname", th.StringType),
        th.Property("lastname", th.StringType),
    )
]

class TicketsStream(GorgiasStream):
    """Define custom stream."""

    name = "tickets"
    path = "/api/tickets"
    primary_keys = ["id"]
    replication_key = "updated_datetime"

    schema = th.PropertiesList(
        th.Property("id", th.IntegerType),
        th.Property("uri", th.StringType),
        th.Property("external_id", th.StringType),
        th.Property("language", th.StringType),
        th.Property("status", th.StringType),
        th.Property("priority", th.StringType),
        th.Property("channel", th.StringType),
        th.Property("via", th.StringType),
        th.Property("from_agent", th.BooleanType),
        th.Property("requester", *CUSTOMER_SCHEMA),
        th.Property("customer", *CUSTOMER_SCHEMA),
        th.Property("assignee_user", *CUSTOMER_SCHEMA),
        th.Property(
            "assignee_team",
            th.ObjectType(
                th.Property("id", th.IntegerType),
                th.Property("name", th.StringType),
                th.Property(
                    "decoration",
                    th.ObjectType(
                        th.Property(
                            "emoji",
                            th.ObjectType(
                                th.Property("id", th.StringType),
                                th.Property("name", th.StringType),
                                th.Property("skin", th.IntegerType),
                                th.Property("colons", th.StringType),
                                th.Property("native", th.StringType),
                                th.Property("unified", th.StringType),
                            ),
                        )
                    ),
                ),
            ),
        ),
        th.Property("subject", th.StringType),
        th.Property("excerpt", th.StringType),
        th.Property(
            "integrations",
            th.ArrayType(
                th.ObjectType(
                    th.Property("name", th.StringType),
                    th.Property("address", th.StringType),
                    th.Property("type", th.StringType),
                )
            ),
        ),
        th.Property(
            "tags",
            th.ArrayType(
                th.ObjectType(
                    th.Property("id", th.IntegerType),
                    th.Property("name", th.StringType),
                    th.Property("uri", th.StringType),
                )
            ),
        ),
        th.Property("messages_count", th.IntegerType),
        th.Property("is_unread", th.BooleanType),
        th.Property("created_datetime", th.DateTimeType),
        th.Property("opened_datetime", th.DateTimeType),
        th.Property("last_received_message_datetime", th.DateTimeType),
        th.Property("last_message_datetime", th.DateTimeType),
        th.Property("updated_datetime", th.DateTimeType),
        th.Property("closed_datetime", th.DateTimeType),
        th.Property("snooze_datetime", th.DateTimeType),
    ).to_dict()

    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        """Return the ticket_id for use by child streams."""
        return {"ticket_id": record["id"]}


class TicketDetailsStream(GorgiasStream):
    """Uses tickets as a parent stream. This stream is used to get the details of a ticket which are not available
    in the List Ticket view, like spam or integration details."""

    name = "ticket_details"
    parent_stream_type = TicketsStream
    path = "/api/tickets/{ticket_id}"
    primary_keys = ["id"]
    state_partitioning_keys = []

    schema = th.PropertiesList(
        th.Property("id", th.IntegerType),
        th.Property(
            "assignee_user",
            th.ObjectType(
                th.Property("id", th.IntegerType),
                th.Property("email", th.StringType),
                th.Property("name", th.StringType),
                th.Property("first_name", th.StringType),
                th.Property("last_name", th.StringType),
            ),
        ),
        th.Property("channel", th.StringType),
        th.Property("closed_datetime", th.DateTimeType),
        th.Property("created_datetime", th.DateTimeType),
        th.Property(
            "customer",
            th.ObjectType(
                th.Property("id", th.IntegerType),
                th.Property("name", th.StringType),
                th.Property("email", th.StringType),
                th.Property(
                    "integrations",
                    th.ObjectType(
                        th.Property(
                            "shopify",
                            th.ObjectType(
                                th.Property("id", th.IntegerType),
                                th.Property(
                                    "orders",
                                    th.ArrayType(
                                        th.ObjectType(
                                            th.Property("id", th.IntegerType),
                                            th.Property("name", th.StringType),
                                            th.Property(
                                                "line_items",
                                                th.ArrayType(
                                                    th.ObjectType(
                                                        th.Property("id", th.IntegerType),
                                                    ),
                                                )
                                            ),
                                        ),
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
            ),
        ),
        th.Property(
            "events",
            th.ArrayType(
                th.ObjectType(
                    th.Property("id", th.IntegerType),
                    th.Property("context", th.StringType),
                    th.Property("created_datetime", th.DateTimeType),
                    th.Property("object_id", th.IntegerType),
                    th.Property("date", th.DateTimeType),
                    th.Property("object_type", th.StringType),
                    th.Property("type", th.StringType),
                    th.Property("user_id", th.IntegerType),
                    th.Property("uri", th.StringType),
                )
            ),
        ),
        th.Property("external_id", th.StringType),
        th.Property("from_agent", th.BooleanType),
        th.Property("is_unread", th.BooleanType),
        th.Property("language", th.StringType),
        th.Property("last_message_datetime", th.DateTimeType),
        th.Property("last_received_message_datetime", th.DateTimeType),
        th.Property("opened_datetime", th.DateTimeType),
        th.Property("priority", th.StringType),
        th.Property("snooze_datetime", th.DateTimeType),
        th.Property("spam", th.BooleanType),
        th.Property("status", th.StringType),
        th.Property("subject", th.StringType),
        th.Property(
            "tags",
            th.ArrayType(
                th.ObjectType(
                    th.Property("id", th.IntegerType),
                    th.Property("name", th.StringType),
                    th.Property("decoration", th.ObjectType(th.Property("color", th.StringType))),
                )
            ),
        ),
        th.Property("trashed_datetime", th.DateTimeType),
        th.Property("updated_datetime", th.DateTimeType),
        th.Property("via", th.StringType),
        th.Property("uri", th.StringType),
    ).to_dict()

    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Override parent URL params with no paging as we only grab a single ticket here."""
        return {}
    
    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """
        Parse the response and swap dynamic keys (id) by a fixed one ("shopify"),
        so every response conforms to the same schema. Add original key as a value
        nested one level bellow.

        Args: response: A raw `requests.Response`_ object.

        Yields: One item for every item found in the response.
        """
        resp = response.json()
        for key in list(resp["customer"]["integrations"].keys()):
            if resp["customer"]["integrations"][key]["__integration_type__"] == "shopify":
                resp["customer"]["integrations"]["shopify"] = resp["customer"]["integrations"].pop(key)
                resp["customer"]["integrations"]["shopify"]["id"] = key
        yield resp

    def post_process(self, row: dict, context: Optional[dict] = None) -> Optional[dict]:
        """
        Remove the ticket and related messages html as it messes up json serialization.
        We can load these via the Messages stream if needed.
        """
        row.pop("body_text", None)
        row.pop("body_html", None)
        row.pop("stripped_text", None)
        row.pop("stripped_html", None)

        for message in row["messages"]:
            message.pop("body_text", None)
            message.pop("body_html", None)
            message.pop("stripped_text", None)
            message.pop("stripped_html", None)
        return row


class MessagesStream(GorgiasStream):
    """Messages stream.

    Uses tickets as a parent stream. Consequently, only retrieves
    messages for tickets included in the ticket view. The ticket
    view contains filters for last_message_datetime and
    last_received_message_datetime to capture all new messages.
    """

    name = "messages"
    parent_stream_type = TicketsStream
    path = "/api/tickets/{ticket_id}/messages"
    primary_keys = ["id"]
    state_partitioning_keys = []

    schema = th.PropertiesList(
        th.Property(
            "id",
            th.IntegerType,
        ),
        th.Property(
            "uri",
            th.StringType,
        ),
        th.Property(
            "message_id",
            th.StringType,
        ),
        th.Property(
            "ticket_id",
            th.IntegerType,
        ),
        th.Property(
            "external_id",
            th.StringType,
        ),
        th.Property("public", th.BooleanType),
        th.Property(
            "channel",
            th.StringType,
        ),
        th.Property(
            "via",
            th.StringType,
        ),
        th.Property(
            "source",
            th.ObjectType(
                th.Property("type", th.StringType),
                th.Property(
                    "to",
                    th.ArrayType(
                        th.ObjectType(
                            th.Property("name", th.StringType),
                            th.Property("address", th.StringType),
                        )
                    ),
                ),
                th.Property(
                    "from",
                    th.ObjectType(
                        th.Property("name", th.StringType),
                        th.Property("address", th.StringType),
                    ),
                ),
            ),
        ),
        th.Property("sender", *CUSTOMER_SCHEMA),
        th.Property(
            "integration_id",
            th.IntegerType,
        ),
        th.Property(
            "rule_id",
            th.IntegerType,
        ),
        th.Property("from_agent", th.BooleanType),
        th.Property("receiver", *CUSTOMER_SCHEMA),
        th.Property(
            "subject",
            th.StringType,
        ),
        th.Property(
            "body_text",
            th.StringType,
        ),
        th.Property(
            "body_html",
            th.StringType,
        ),
        th.Property(
            "stripped_text",
            th.StringType,
        ),
        th.Property(
            "stripped_html",
            th.StringType,
        ),
        th.Property(
            "stripped_signature",
            th.StringType,
        ),
        # th.Property(
        #     "actions",
        #     th.ArrayType(
        #         th.ObjectType()
        #     ),
        # ),
        th.Property(
            "created_datetime",
            th.DateTimeType,
        ),
        th.Property("sent_datetime", th.DateTimeType),
        th.Property("failed_datetime", th.DateTimeType),
        th.Property("deleted_datetime", th.DateTimeType),
        th.Property("opened_datetime", th.DateTimeType),
    ).to_dict()


class SatisfactionSurveysStream(GorgiasStream):
    """Satisfaction surveys.

    The satisfaction survey API endpoint does not allow any filtering or
    custom ordering of the results. It also has no cursor, so if records
    are added while paging through the results, records will be missed.
    This has to be run as a full refresh for each extraction, due to the
    inability to filter and lack of clear updated_datetime field on the
    survey object.
    https://developers.gorgias.com/reference/the-satisfactionsurvey-object
    https://developers.gorgias.com/reference/get_api-satisfaction-surveys
    """

    name = "satisfaction_surveys"
    path = "/api/satisfaction-surveys"

    primary_keys = ["id"]
    schema = th.PropertiesList(
        th.Property("id", th.IntegerType),
        th.Property("body_text", th.StringType),
        th.Property("created_datetime", th.DateTimeType),
        th.Property("customer_id", th.IntegerType),
        th.Property("score", th.IntegerType),
        th.Property("scored_datetime", th.DateTimeType),
        th.Property("sent_datetime", th.DateTimeType),
        th.Property("should_send_datetime", th.DateTimeType),
        th.Property("ticket_id", th.IntegerType),
        th.Property("uri", th.StringType),
    ).to_dict()


class CustomersStream(GorgiasStream):
    """Customers.

    The customers API endpoint does not allow any filtering or
    custom ordering of the results, only on created datetime.
    This has to be run as a full refresh for each extraction, due to the
    inability to filter and lack of ordering by updated_datetime..
    https://developers.gorgias.com/reference/get_api-customers
    """

    name = "customers"
    path = "/api/customers"
    primary_keys = ["id"]

    schema = th.PropertiesList(
        th.Property("id", th.IntegerType),
        th.Property("created_datetime", th.DateTimeType),
        th.Property("email", th.StringType),
        th.Property("external_id", th.StringType),
        th.Property("firstname", th.StringType),
        th.Property("language", th.StringType),
        th.Property("lastname", th.StringType),
        th.Property("name", th.StringType),
        th.Property("timezone", th.StringType),
        th.Property("updated_datetime", th.DateTimeType),
        th.Property("note", th.StringType),
        th.Property("active", th.BooleanType),
        th.Property(
            "meta",
            th.ObjectType(
                th.Property("name_set_via", th.StringType),
            ),
        ),
        th.Property("error", th.StringType),
    ).to_dict()


class IntegreationsStream(GorgiasStream):
    name = "integrations"
    path = "/api/integrations"
    primary_keys = ["id"]

    # Link to the next items, if any.
    next_page_token_jsonpath = "$.meta.next_items"

    schema = th.PropertiesList(
        th.Property("id", th.IntegerType),
        th.Property("uri", th.StringType),
        th.Property(
            "user",
            th.ObjectType(th.Property("id", th.IntegerType)),
        ),
        th.Property("type", th.StringType),
        th.Property("name", th.StringType),
        th.Property("description", th.StringType),
        th.Property(
            "meta",
            th.ObjectType(
                th.Property("shop_name", th.StringType),
                th.Property("shop_display_name", th.StringType),
                th.Property("shop_domain", th.StringType),
                th.Property("shop_plan", th.StringType),
                th.Property("shop_id", th.IntegerType),
                th.Property("shopify_integration_ids", th.ArrayType(th.IntegerType)),
                th.Property("shopify_integration_id", th.IntegerType),
                th.Property("shop_integration_id", th.IntegerType),
            ),
        ),
        th.Property("created_datetime", th.DateTimeType),
        th.Property("updated_datetime", th.DateTimeType),
        th.Property("deactivated_datetime", th.DateTimeType),
        th.Property("locked_datetime", th.DateTimeType),
        th.Property("deleted_datetime", th.DateTimeType),
    ).to_dict()
