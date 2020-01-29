"""
This module handles the creation of webhook subscriptions. It creates
a subscription to receive webhooks for a particular event_type.
"""
from k2connect import exceptions
from k2connect import json_builder
from k2connect import service
from k2connect import validation

WEBHOOK_SUBSCRIPTION_PATH = 'api/v1/webhook_subscriptions'


class WebhookService(service.Service):
    """
    The WebhookService class contains methods for the creation of a webhook
    subscription.
    Example:
        # initialize webhook service
        >>> k2-connect.WebhookService
        >>> k2-connect.create_subscription('buygoods_transaction_reversed',
        >>>................................'https://myapplication/webhooks',
        >>>................................os.getenv('SOME_UNCRACKABLE_SECRET'))

    """

    def __init__(self, base_url):
        """
        :param base_url:
        :type  base_url: str
        """
        super(WebhookService, self).__init__(base_url)

    def create_subscription(self,
                            bearer_token,
                            event_type,
                            webhook_endpoint,
                            webhook_secret):
        """
        Creates a subscription to a webhook service.
        Returns a request response object < class, 'requests.models.Response'>
        :param bearer_token: Access token to be used to make calls to
        the Kopo Kopo API
        :type bearer_token: str
        :param event_type:Type of subscription event. Should be one of:
        buygoods_transaction_received, buygoods_transaction_reversed,
        settlement_transfer_completed, customer_created
        :type event_type:  str
        :param webhook_endpoint: HTTP end point to send the webhook.
        :type webhook_endpoint: str
        :param webhook_secret: Secret used to encrypt the request payload using HMAC.
        :type webhook_secret: str
        :return: requests.models.Response
        """
        # event types
        event_types_to_check = ['b2b_transaction_received',
                                'buygoods_transaction_received',
                                'buygoods_transaction_reversed',
                                'merchant_to_merchant_transaction_received',
                                'settlement_transfer_completed',
                                'customer_created'
                                ]
        # build subscription url
        subscription_url = self._build_url(WEBHOOK_SUBSCRIPTION_PATH)

        # define headers
        headers = dict(self.headers)

        # validate string arguments
        validation.validate_string_arguments(bearer_token,
                                             event_type,
                                             webhook_endpoint,
                                             webhook_secret)

        headers['Authorization'] = 'Bearer ' + bearer_token + ''

        if not any(check in event_type for check in event_types_to_check):
            raise exceptions.InvalidArgumentError('Event type not recognized by k2-connect')

        # validate webhook endpoint
        validation.validate_url(webhook_endpoint)
        
        # define subscription payload
        subscription_payload = json_builder.webhook_subscription(event_type=event_type,
                                                                 webhook_endpoint=webhook_endpoint,
                                                                 webhook_secret=webhook_secret)

        return self._make_requests(headers=headers,
                                   method='POST',
                                   url=subscription_url,
                                   payload=subscription_payload)
