"""Handles transfer of funds to pre-approved settlement accounts (bank accounts or mobile wallets)."""
import requests
from k2client.json_builder import amount, transfers, bank_account
from .service import Service

# for sandbox:
# https://api-sandbox.kopokopo.com/transfers
# https://api-sandbox.kopokopo.com/merchant_bank_accounts
# for production:
# https://api.kopokopo.com/transfers
# https://api.kopokopo.com/merchant_bank_accounts

transfers_path = "transfers"
settlement_accounts_path = "merchant_bank_accounts"


class TransferService(Service):
    def __init__(self, bearer_token):
        """
        :param bearer_token:
        """
        super(TransferService, self).__init__(client_id=self._client_id, client_secret=self._client_secret)
        self._bearer_token = bearer_token
        self.transfer_currency = transfer_currency
        self.transfer_value = transfer_value
        self.transfer_destination = transfer_destination

    # add a verified settlement account
    def add_settlement_account(self,
                               account_name,
                               bank_ref,
                               bank_branch_ref,
                               account_number):
        """
        :param account_name:
        :param bank_ref:
        :param bank_branch_ref:
        :param account_number:
        :return:
        """

        # build add transfer path
        url = self.build_url(settlement_accounts_path)

        payload = bank_account(account_name=account_name,
                               bank_ref=bank_ref,
                               bank_branch_ref=bank_branch_ref,
                               account_number=account_number)

        return self.make_requests(url=url, method='POST', payload=payload, headers=self._headers)

    def settle_funds(self, transfer_currency, transfer_value, transfer_destination=None):
        """
        :param transfer_currency:
        :param transfer_value:
        :param transfer_destination:
        :return:
        """

        # build url for settle funds
        url = self.build_url(transfers_path)

        # define amount json object
        transfer_amount = amount(currency=transfer_currency, value=transfer_value)

        if transfer_destination is None:
            # define blind transfer json
            payload = transfers(amount=transfer_amount)

            return self.make_requests(url=url, method='POST', payload=payload, headers=self._headers)
        else:
            # define targeted transfer json
            payload = transfer_object(amount=transfer_amount, destination=transfer_destination)

        return self.make_requests(url=url, method='POST', payload=payload, headers=self._headers)

    def transfer_status(self, response):
        """
        :param response:
        :return:
        """
        # define query location
        query_location = ResourceLocation(response).get_location()

        # define query status object
        query_status_object = QueryStatus(bearer_token=self._bearer_token)

        return query_status_object.query_transaction_status(query_location)
