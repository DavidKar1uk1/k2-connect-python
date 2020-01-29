"""
This module handles the k2-connect PAY service. It entails the creation
of payments and pay recipients within the pay service. Once a transaction
is created, the service provides the user with a means to query k2 servers
for the pay transaction's status.
"""
from k2connect import service
from k2connect import json_builder
from k2connect import exceptions
from k2connect import validation

# PAY Service paths
ADD_PAY_PATH = "api/v1/pay_recipients"
SEND_PAY_PATH = "api/v1/payments"

# PAY recipient types
BANK_ACCOUNT_RECIPIENT_TYPE = "bank_account"
MOBILE_WALLET_RECIPIENT_TYPE = "mobile_wallet"


class PayService(service.Service):
    """
    The PayService class containing methods to:
    To create pay recipients
    Example:
        >>>import k2connect
        >>>k2connect.initialize('sample_client_id', 'sample_client_secret', 'https://some_url.com/')
        >>> pay = k2-connect.Pay
        >>> pay_recipient = pay.add_pay_recipient(recipient_type='mobile_wallet',
        >>>.......................................first_name='Jaqen',
        >>>.......................................last_name='Hghar',
        >>>.......................................phone='+007856798451',
        >>>.......................................network='Valyria Mobile')
    To send payments to third parties
    Example:
        >>> pay_transaction = pay.send_pay('https://mycoolapp.com',
        >>>................................'c7f300c0-f1ef-4151-9bbe-005005aa3747',
        >>>................................'25000',
        >>>................................customerId='8675309',
        >>>................................notes='Salary payment for May 2018')
    To check transaction statuses
    Example:
        >>> pay.transaction status(pay_transaction)
        '{"status":"Scheduled","reference":"KKKKKKKKK",
        "origination_time":"2018-07-20T22:45:12.790Z",
        "destination":"c7f300c0-f1ef-4151-9bbe-005005aa3747",
        "amount":{"currency":"KES","value":20000},"
        metadata":{"customerId":"8675309",
        "notes":"Salary payment for May 2018"},
        "_links":{"self":"https://api-sandbox.kopokopo.com/payments
        /d76265cd-0951-e511-80da-0aa34a9b2388"}}'
    get payment request location
    Example:object
        >>> pay.pay_transaction_location(pay_transaction)
        'https://api-sandbox.kopokopo.com/payments/c7f300c0-f1ef-4151-9bbe-005005aa3747'
    """

    def __init__(self, base_url):
        """

        :param base_url: The domain to use in the library.
        :type base_url: str
        """
        super(PayService, self).__init__(base_url=base_url)

    def add_pay_recipient(self,
                          bearer_token,
                          recipient_type,
                          **kwargs):
        """
        Adds external entities that will be the destination of your payments.
        Returns a request response object < class, 'requests.models.Response'>
        :param bearer_token: Access token to be used to make calls to
        the Kopo Kopo API
        :type bearer_token: str
        :param recipient_type: The type of wallet to which pay will be sent.
                Example:
                    recipient_type = BANK_ACCOUNT_RECIPIENT_TYPE
        :type recipient_type: str
        :param kwargs: The values thAccess token to be used to make calls to
        the Kopo Kopo APIat constitute recipient types.
        :type kwargs: dict

        :return:'requests.models.Response'
        """
        # define headers
        headers = dict(self._headers)

        validation.validate_string_arguments(bearer_token)

        # add bearer token
        headers['Authorization'] = 'Bearer ' + bearer_token + ''

        # build url
        add_pay_url = self._build_url(url_path=ADD_PAY_PATH)

        if 'email' in kwargs:
            validation.validate_email(str(kwargs['email']))
        if 'phone' in kwargs:
            validation.validate_phone_number(str(kwargs['phone']))

        # expected parameters for bank account wallet recipient
        # ['account_name', 'account_number',
        # 'bank_branch_id','bank_id', name']
        if recipient_type == BANK_ACCOUNT_RECIPIENT_TYPE:
            if 'account_name' not in kwargs or \
                    'account_number' not in kwargs or \
                    'bank_branch_id' not in kwargs or \
                    'bank_id' not in kwargs or \
                    'name' not in kwargs:
                raise exceptions.InvalidArgumentError('Invalid arguments for bank account')

            # build recipient json object
            recipient_object = json_builder.bank_account(account_name=str(kwargs['account_name']),
                                                         account_number=str(kwargs['account_number']),
                                                         bank_branch_id=str(kwargs['bank_branch_id']),
                                                         bank_id=str(kwargs['bank_id']),
                                                         name=str(kwargs['name']),
                                                         email=None,
                                                         phone=None)

            # build bank payment recipient json object
            payment_recipient_object = json_builder.pay_recipient(recipient_type=recipient_type,
                                                                  recipient=recipient_object)
        # expected parameters for mobile wallet recipient
        # ['first_name', 'last_name',
        # network','phone','email']

        elif recipient_type == MOBILE_WALLET_RECIPIENT_TYPE:
            if 'first_name' not in kwargs or \
                    'last_name' not in kwargs or \
                    'phone' not in kwargs or \
                    'network' not in kwargs:
                raise exceptions.InvalidArgumentError('Invalid arguments for mobile wallet')

            # create recipient json object
            recipient_object = json_builder.mobile_wallet(first_name=str(kwargs['first_name']),
                                                          last_name=str(kwargs['last_name']),
                                                          phone=str(kwargs['phone']),
                                                          network=str(kwargs['network']),
                                                          email=None)

            # create mobile wallet recipient json object
            payment_recipient_object = json_builder.pay_recipient(recipient_type=recipient_type,
                                                                  recipient=recipient_object)
        else:
            raise exceptions.InvalidArgumentError('The recipient type is not recognized by k2connect')

        return self._make_requests(headers=headers,
                                   method='POST',
                                   payload=payment_recipient_object,
                                   url=add_pay_url, )

    def send_pay(self,
                 bearer_token,
                 callback_url,
                 destination,
                 value,
                 currency='KES',
                 **kwargs):
        """
        Creates an outgoing pay to a third party. The result of
        the pay is provided asynchronously and posted to the callback_url
        provided.
        Returns a request response object < class, 'requests.models.Response'>
        :param bearer_token: Access token to be used to make calls to
        the Kopo Kopo API
        :type bearer_token: str
        :param callback_url:
        :type callback_url: str
        :param destination: ID of the destination of funds.
        :type destination: str
        :param value: Value of money to be sent (child of amount JSON str)
        :type value: str
        :param currency: Currency of amount being transacted
        :type currency: str
        :param kwargs: Provision for optional metadata with maximum of 5
        key value pairs.
        :type kwargs: dict

        :return:requests.models.Response
        """
        # build send_pay url
        send_pay_url = self._build_url(SEND_PAY_PATH)

        # define headers
        headers = dict(self.headers)

        # check bearer token
        validation.validate_string_arguments(bearer_token)

        # add authorization to headers
        headers['Authorization'] = 'Bearer ' + bearer_token + ''

        # create amount json object
        pay_amount = json_builder.amount(currency=currency,
                                         value=value)

        # create metadata json object
        pay_metadata = json_builder.metadata(', '.join(['{}={}'.format(k, v)
                                                        for k, v in kwargs.items()]))

        # create links json object
        pay_links = json_builder.links(callback_url=callback_url)

        # create payment json object
        pay_json = json_builder.pay(destination,
                                    pay_amount,
                                    pay_metadata,
                                    pay_links)

        return self._make_requests(url=send_pay_url,
                                   method='POST',
                                   payload=pay_json,
                                   headers=headers)

    def pay_transaction_status(self,
                               bearer_token,
                               query_url):
        """
        Returns a JSON object result containing the transaction status.
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
    def pay_transaction_location(response):
        """
        Returns location of the pay transaction result as returned in the headers of the
        response body.
        :param response: response object from a HTTP request
        :type response: requests.models.Response
        :return str
        """
        return service.k2_requests.get_location(response)
