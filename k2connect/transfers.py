"""
This module handles transfer of funds to pre-approved settlement accounts. It creates
verified settlement bank accounts. Once an account to which funds can be settled is available,
it creates blind and targeted settlement transactions.
Blind transfers are made to the default settlement account defined upon k2 customer acquisition,
targeted transfers are made to a defined destination account.
"""
from k2connect import json_builder
from k2connect import service
from k2connect import validation

TRANSFER_PATH = 'api/v1/transfers'
SETTLEMENT_ACCOUNTS_PATH = 'api/v1/merchant_bank_accounts'


class TransferService(service.Service):
    """
    The TransferService class containing methods for creation of settlement accounts:
    Example:
        # initialize transfer service
        >>> k2connect.TransferService
        >>> k2connect.add_settlement_account('Arya Stark',
        >>>.....................................'45164-IRON BANK',
        >>>.....................................'78491631254523',
        >>>.....................................'564123456987845')
    """

    def __init__(self, base_url):
        """
        Initializes transfer services with the bearer token as an argument.
        This feature allows the developer to refresh the access token
        at any point in their codebase.
        :param bearer_token: Access token to be used to make calls to
        the Kopo Kopo API
        :type  bearer_token: str
        """
        super(TransferService, self).__init__(base_url)

    def add_settlement_account(self,
                               bearer_token,
                               account_name,
                               account_number,
                               bank_ref,
                               bank_branch_ref):
        """
        Creates a verified settlement bank account.
        Returns a request response object < class, 'requests.models.Response'>
        :param bearer_token
        :type bearer_token: str
        :param account_name: The name as indicated on the bank account name
        :type account_name: str
        :param bank_ref: An identifier identifying the destination bank
        :type bank_ref: str
        :param bank_branch_ref: An identifier identifying the destination bank branch
        :type bank_branch_ref: str
        :param account_number: The bank account number
        :type account_number: str
        :return: requests.models.Response
        """
        # build url
        create_settlement_account_url = self._build_url(SETTLEMENT_ACCOUNTS_PATH)

        # validate string arguments
        validation.validate_string_arguments(bearer_token,
                                             account_name,
                                             bank_ref,
                                             bank_branch_ref,
                                             account_number)

        # add authorization to headers
        headers['Authorization'] = 'Bearer ' + bearer_token + ''

        # define create settlement account payload
        create_settlement_account_payload = json_builder.bank_settlement_account(account_name=account_name,
                                                                                 account_number=account_number,
                                                                                 bank_branch_ref=bank_branch_ref,
                                                                                 bank_ref=bank_ref)
        return self._make_requests(headers=headers,
                                   method='POST',
                                   url=create_settlement_account_url,
                                   payload=create_settlement_account_payload)

    def settle_funds(self,
                     bearer_token,
                     transfer_value,
                     transfer_currency='KES',
                     transfer_destination=None):
        """
        Creates a transfer from merchant account to a different settlement account.
        Returns a request response object < class, 'requests.models.Response'>
        :param bearer_token: Access token to be used to make calls to
        the Kopo Kopo API
        :type bearer_token: str
        :param transfer_currency: Currency of amount being transacted
        :type transfer_currency: str
        :param transfer_value:
        :type transfer_value:Value of money to be sent.
        :param transfer_destination: str
        :type transfer_destination: ID of the destination of funds
        :return: requests.models.Response
        """
        # build settle funds url
        settle_funds_url = self._build_url(TRANSFER_PATH)

        # define headers
        headers = dict(self.headers)

        # check bearer token
        validation.validate_string_arguments(bearer_token,
                                             transfer_currency,
                                             transfer_value)

        # add authorization to headers
        headers['Authorization'] = 'Bearer ' + bearer_token + ''

        # define amount
        transfer_amount = json_builder.amount(currency=transfer_currency,
                                              value=transfer_value)

        if transfer_destination is None:
            settle_funds_payload = json_builder.transfers(transfers_amount=transfer_amount)
        else:
            settle_funds_payload = json_builder.transfers(transfers_amount=transfer_amount,
                                                          transfer_destination=transfer_destination)
        return self._make_requests(headers=headers,
                                   method='POST',
                                   url=settle_funds_url,
                                   payload=settle_funds_payload)

    def transfer_transaction_status(self,
                                    bearer_token,
                                    query_url):
        """
        Returns a JSON object result containing the transaction status.
        :param bearer_token: Access token to be used to make calls to
        the Kopo Kopo API.
        :type bearer_token: str
        :param query_url: URL to which status query is made.
        :type query_url: str
        :return str
        """
        return self._query_transaction_status(bearer_token=bearer_token,
                                              query_url=query_url)

    @staticmethod
    def transfer_transaction_location(response):
        """
        Returns location of the transfers transaction result as returned in the headers of the
        response body.
        :param response: response object from a HTTP request
        :type response: requests.models.Response
        :return str
        """
        return service.k2_requests.get_location(response)
