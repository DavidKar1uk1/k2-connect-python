import unittest
from unittest.mock import patch

from tests import SAMPLE_BASE_URL, SAMPLE_CLIENT_ID, SAMPLE_CLIENT_SECRET
from tests.data import headers

from k2connect import authorization
from k2connect import exceptions
from mocks import k2_response_mock


class TokenServiceInitializationTestCase(unittest.TestCase):

    def test_initialization_with_all_arguments_present_succeeds(self):
        token_request = authorization.TokenService(base_url=SAMPLE_BASE_URL,
                                                   client_id=SAMPLE_CLIENT_ID,
                                                   client_secret=SAMPLE_CLIENT_SECRET)
        self.assertIsInstance(token_request, authorization.TokenService)

    def test_initialization_without_base_url_fails(self):
        with self.assertRaises(exceptions.InvalidArgumentError):
            token_request = authorization.TokenService(base_url=None,
                                                       client_id=SAMPLE_CLIENT_ID,
                                                       client_secret=SAMPLE_CLIENT_SECRET)
            self.assertIsInstance(token_request, authorization.TokenService)

    def test_initialization_without_client_id_fails(self):
        with self.assertRaises(exceptions.InvalidArgumentError):
            token_request = authorization.TokenService(base_url=SAMPLE_BASE_URL,
                                                       client_id=None,
                                                       client_secret=SAMPLE_CLIENT_SECRET)
            self.assertIsInstance(token_request, authorization.TokenService)

    def test_initialization_without_client_secret_fails(self):
        with self.assertRaises(exceptions.InvalidArgumentError):
            token_request = authorization.TokenService(base_url=SAMPLE_BASE_URL,
                                                       client_id=SAMPLE_CLIENT_ID,
                                                       client_secret=None)
            self.assertIsInstance(token_request, authorization.TokenService)

    def test_initialization_without_all_arguments_fails(self):
        with self.assertRaises(exceptions.InvalidArgumentError):
            token_request = authorization.TokenService(base_url=None,
                                                       client_id=None,
                                                       client_secret=None)
            self.assertIsInstance(token_request, authorization.TokenService)


class RequestingAccessToken(unittest.TestCase):
    def setUp(self):
        # define response for successful http request
        success_data = open('data/oauth_access_token.json', 'r')
        print(type(success_data.read()))

        self.mock_success_response = k2_response_mock.mock_response(headers=headers.headers,
                                                                    status_code=200,
                                                                    content=success_data,
                                                                    json=success_data)

        success_data.close()

    @patch('k2connect.authorization.TokenService')
    def test_request_access_token_returns_response(self,
                                                   mock_token_service):
        token_request = mock_token_service(base_url=SAMPLE_BASE_URL,
                                           client_id=SAMPLE_CLIENT_ID,
                                           client_secret=SAMPLE_CLIENT_SECRET)

        token_request.request_access_token.return_value = self.mock_success_response

        response = token_request.request_access_token()

        self.assertIsNotNone(response)

    def tearDown(self):
        self.mock_success_response.dispose()


if __name__ == '__main__':
    INITIALIZATION_SUITE = unittest.TestLoader().loadTestsFromTestCase(TokenServiceInitializationTestCase)
    REQUEST_ACCESS_TOKEN_SUITE = unittest.TestLoader().loadTestsFromTestCase(RequestingAccessToken)
    PARENT_SUITE = unittest.TestSuite([INITIALIZATION_SUITE, REQUEST_ACCESS_TOKEN_SUITE])
    unittest.TextTestRunner(verbosity=1).run(PARENT_SUITE)
