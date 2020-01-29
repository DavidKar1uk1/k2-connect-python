import unittest
from k2connect import exceptions
from k2connect import pay
from k2connect import validation
from tests import SAMPLE_BASE_URL


class AddPayRecipientTestCase(unittest.TestCase):

    def test_init_method_with_base_url_argument_succeeds(self):
        pay_service = pay.PayService(base_url=SAMPLE_BASE_URL)
        self.assertIsInstance(pay_service, pay.PayService)