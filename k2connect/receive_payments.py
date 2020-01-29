"""

This module handles k2-connect receive MPESA payments service. It facilitates
the reception of payments from MPESA users. It creates requests for the reception
of MPESA payments. Succeeding a MPESA payment request, it queries the status of the
transaction.
"""
from k2connect import exceptions
from k2connect import json_builder
from k2connect import k2_requests
from k2connect import service
from k2connect import validation

CREATE_RECEIVE_MPESA_PAYMENT_PATH = 'api/v1/incoming_payments'


class ReceivePaymentsService(service.Service):
    """
    The ReceivePaymentsService class containing methods to create requests for
    MPESA payments:
    Example:
        >>>import k2connect
        >>>k2connect.initialize('sample_client_id', 'sample_client_secret', 'https://some_url.com/')
        >>>mpesa_payment = k2connect.ReceiveMpesaPayments
        >>>mpesa_payment_request = mpesa_payment.create_payment_request('bearer_token',
        >>>....................................................................'callback_url',
        >>>....................................................................'currency',
        >>>....................................................................'first_name',
        >>>....................................................................'last_name',
        >>>....................................................................'payment_channel',
        >>>....................................................................'phone',
        >>>....................................................................'till_number',
        >>>....................................................................'value')

    To check payment request status:
    Example:
        >>>payment_status = mpesa_payment.payment_request_status('bearer_token',
        >>>......................................................'query_url')

    To check payment request location:
    Example:
        >>>payment_location = mpesa_payment.payment_request_location('response')
    """

    def __init__(self, base_url):
        """
        :param base_url: The domain to use in the library
        :type  base_url: str
        """
        super(ReceivePaymentsService, self).__init__(base_url=base_url)

    # noinspection PyArgumentList
    def create_payment_request(self,
                               bearer_token,
                               callback_url,
                               first_name,
                               last_name,
                               payment_channel,
                               phone,
                               till_number,
                               value,
                               currency='KES',
                               **kwargs):
        """
        Creates a request for the reception of payments from MPESA users.
        Returns a request response object < class, 'requests.models.Response'>
        :param bearer_token: Access token to be used to make calls to
        the Kopo Kopo API.
        :type bearer_token: str
        :param callback_url: Callback URL where the result of the MPESA payment
        request will be posted.
        :type callback_url: str
        :param currency: Currency of amount being transacted
        :type currency: str
        :param first_name: First name of the subscriber.
        :type first_name: str
        :param last_name: Last name of the subscriber.
        :type last_name: str
        :param phone: Phone number of the subscriber from which the payment will
        be made.
        :type phone: str
        :param payment_channel: Payment channel to be used eg. MPESA.
        :type payment_channel: str
        :param till_number: Till to which the payment will be made.
        :type till_number: str
        :param value: Value of money to be received
        :type value: str
        :param kwargs:
        :type kwargs: dict
        :return: requests.models.Response
        """
        # validate phone number
        if validation.validate_phone_number(phone) is False:
            pass

        # validate email address if present
        if 'email' in kwargs:
            validation.validate_email(str(kwargs['email']))
            email = kwargs['email']
        else:
            email = 'Null'

        # define headers
        headers = dict(self.headers)

        # validate bearer_token
        validation.validate_string_arguments(bearer_token)

        # add bearer token
        headers['Authorization'] = 'Bearer ' + bearer_token + ''

        # build create mpesa payment request url
        mpesa_payment_request_url = self._build_url(CREATE_RECEIVE_MPESA_PAYMENT_PATH)

        # define amount JSON object
        mpesa_payment_request_amount = json_builder.amount(currency=currency,
                                                           value=value)

        # define links JSON object
        mpesa_payment_request_links = json_builder.links(callback_url=callback_url)

        # define metadata JSON object
        mpesa_payment_metadata = json_builder.metadata(', '.join(['{}={}'.format(k, v)
                                                                  for k, v in kwargs.items()]))

        # define subscriber JSON object
        mpesa_payment_subscriber = json_builder.subscriber(first_name=first_name,
                                                           last_name=last_name,
                                                           phone=phone,
                                                           email=email)

        # define MPESA payment request JSON object
        mpesa_payment_request_payload = json_builder.mpesa_payment(mpesa_links=mpesa_payment_request_links,
                                                                   mpesa_payment_amount=mpesa_payment_request_amount,
                                                                   mpesa_payment_subscriber=mpesa_payment_subscriber,
                                                                   metadata=mpesa_payment_metadata,
                                                                   payment_channel=payment_channel,
                                                                   till_number=till_number)
        return self._make_requests(headers=headers,
                                   method='POST',
                                   url=mpesa_payment_request_url,
                                   payload=mpesa_payment_request_payload)

    def payment_request_status(self,
                               bearer_token,
                               query_url):
        """
        Returns a JSON object result containing the payment request status.
        :param bearer_token: Access token to be used to make calls to
        the Kopo Kopo API
        :type bearer_token: str
        :param query_url: URL to which status query is made.
        :type query_url: str
        :return str
        """
        return self._query_transaction_status(bearer_token=bearer_token,
                                              query_url=query_url)

    @staticmethod
    def payment_request_location(response):
        """
        Returns location of the receive mpesa transaction result as returned in the headers of the
        response body.
        :param response: response object from a HTTP request
        :type response: requests.models.Response
        :return str
        """
        return service.k2_requests.get_location(response)
