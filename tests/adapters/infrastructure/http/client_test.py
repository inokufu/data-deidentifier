from unittest.mock import Mock, patch

import pytest
from httpx import HTTPError, HTTPStatusError, Response
from logger import LoggerContract

from src.data_deidentifier.adapters.infrastructure.http.client import (
    BaseHttpClient,
    HttpClientError,
)


def create_mock_response(status_code: int = 200, text: str = "response") -> Mock:
    """Helper to create properly configured mock response."""
    mock_response = Mock(spec=Response)
    mock_response.status_code = status_code
    mock_response.text = text
    mock_response.raise_for_status.return_value = None
    return mock_response


class TestBaseHttpClientRequest:
    """Test request method."""

    @patch("httpx.Client.request")
    def test_request_success_post_method(
        self,
        mock_request: Mock,
        mock_logger: LoggerContract,
    ) -> None:
        """Should make successful POST request with JSON data."""
        # Arrange
        url = "http://example.com/api"
        method = "POST"
        data = {"key": "value"}
        headers = {"Authorization": "Bearer token"}
        timeout = 30

        mock_response = create_mock_response()
        mock_request.return_value = mock_response

        client = BaseHttpClient(logger=mock_logger)

        # Act
        result = client.request(
            url=url,
            method=method,
            data=data,
            headers=headers,
            timeout_seconds=timeout,
        )

        # Assert
        assert result == mock_response
        mock_request.assert_called_once_with(
            method=method,
            url=url,
            json=data,  # POST uses json parameter
            params=None,  # POST doesn't use params
            headers=headers,
            timeout=timeout,
        )

        # Verify logging
        mock_logger.debug.assert_any_call(
            "Making HTTP request",
            {
                "url": url,
                "method": method,
                "timeout_seconds": timeout,
            },
        )
        mock_logger.debug.assert_any_call(
            "HTTP request successful",
            {
                "url": url,
                "status_code": 200,
                "response_size": len("response"),
            },
        )

    @patch("httpx.Client.request")
    def test_request_success_get_method(
        self,
        mock_request: Mock,
        mock_logger: LoggerContract,
    ) -> None:
        """Should make successful GET request with URL params."""
        # Arrange
        url = "http://example.com/api"
        method = "GET"
        data = {"query": "search"}

        mock_response = create_mock_response()
        mock_request.return_value = mock_response

        client = BaseHttpClient(logger=mock_logger)

        # Act
        result = client.request(url=url, method=method, data=data)

        # Assert
        assert result == mock_response
        mock_request.assert_called_once_with(
            method=method,
            url=url,
            json=None,  # GET doesn't use json
            params=data,  # GET uses params
            headers=None,
            timeout=BaseHttpClient.DEFAULT_TIMEOUT,
        )

    @pytest.mark.parametrize("method", ["POST", "PUT", "PATCH"])
    @patch("httpx.Client.request")
    def test_request_methods_with_json_body(
        self,
        mock_request: Mock,
        method: str,
        mock_logger: LoggerContract,
    ) -> None:
        """Should use JSON body for POST, PUT, PATCH methods."""
        # Arrange
        url = "http://example.com/api"
        data = {"key": "value"}

        mock_response = create_mock_response()
        mock_request.return_value = mock_response

        client = BaseHttpClient(logger=mock_logger)

        # Act
        client.request(url=url, method=method, data=data)

        # Assert
        mock_request.assert_called_once_with(
            method=method,
            url=url,
            json=data,  # These methods use json
            params=None,
            headers=None,
            timeout=BaseHttpClient.DEFAULT_TIMEOUT,
        )

    @patch("httpx.Client.request")
    def test_request_http_error_raises_client_error(
        self,
        mock_request: Mock,
        mock_logger: LoggerContract,
    ) -> None:
        """Should raise HttpClientError when HTTPError occurs."""
        # Arrange
        url = "http://example.com/api"
        http_error = HTTPError("Connection failed")
        mock_request.side_effect = http_error

        client = BaseHttpClient(logger=mock_logger)

        # Act & Assert
        with pytest.raises(HttpClientError, match="HTTP error occurred"):
            client.request(url=url, method="GET", data={})

        # Verify error logging
        mock_logger.exception.assert_called_once_with(
            "HTTP error occurred",
            http_error,
            {
                "url": url,
                "method": "GET",
                "timeout_seconds": BaseHttpClient.DEFAULT_TIMEOUT,
            },
        )

    @patch("httpx.Client.request")
    def test_request_http_status_error_raises_for_status(
        self,
        mock_request: Mock,
        mock_logger: LoggerContract,
    ) -> None:
        """Should call raise_for_status and handle status errors."""
        # Arrange
        mock_response = create_mock_response()
        mock_response.raise_for_status.side_effect = HTTPError("404 Not Found")
        mock_request.return_value = mock_response

        client = BaseHttpClient(logger=mock_logger)

        # Act & Assert
        with pytest.raises(HttpClientError):
            client.request(url="http://example.com", method="GET", data={})

        mock_response.raise_for_status.assert_called_once()


class TestBaseHttpClientRetryLogic:
    """Test retry behavior."""

    @patch("tenacity.time.sleep")  # Speed up test by mocking sleep
    @patch("httpx.Client.request")
    def test_retry_on_server_error_then_success(
        self,
        mock_request: Mock,
        mock_sleep: Mock,
        mock_logger: LoggerContract,
    ) -> None:
        """Should retry on 5xx server errors and succeed eventually."""
        # Arrange
        server_response = create_mock_response(status_code=500)
        server_error = HTTPStatusError(
            "Server Error",
            request=Mock(),
            response=server_response,
        )
        success_response = create_mock_response()

        # Fail twice with 500, then succeed
        mock_request.side_effect = [server_error, server_error, success_response]

        client = BaseHttpClient(logger=mock_logger)

        # Act
        result = client.request(url="http://example.com", method="GET", data={})

        # Assert
        assert result == success_response
        assert mock_request.call_count == 3  # Initial + 2 retries

    @patch("tenacity.time.sleep")  # Speed up test by mocking sleep
    @patch("httpx.Client.request")
    def test_retry_exhausted_raises_error(
        self,
        mock_request: Mock,
        mock_sleep: Mock,
        mock_logger: LoggerContract,
    ) -> None:
        """Should raise error after all retry attempts are exhausted."""
        # Arrange
        server_response = create_mock_response(status_code=503)
        server_error = HTTPStatusError(
            "Service Unavailable",
            request=Mock(),
            response=server_response,
        )

        mock_request.side_effect = server_error  # Always fail

        client = BaseHttpClient(logger=mock_logger)

        # Act & Assert
        with pytest.raises(HttpClientError):
            client.request(url="http://example.com", method="GET", data={})

        # Should try 3 times total (initial + 2 retries)
        assert mock_request.call_count == 3

    @patch("httpx.Client.request")
    def test_no_retry_on_client_error(
        self,
        mock_request: Mock,
        mock_logger: LoggerContract,
    ) -> None:
        """Should not retry requests when client error occurs."""
        # Arrange
        mock_response = create_mock_response(status_code=404)
        client_error = HTTPStatusError(
            "Not Found",
            request=Mock(),
            response=mock_response,
        )
        mock_request.side_effect = client_error

        client = BaseHttpClient(logger=mock_logger)

        # Act & Assert
        with pytest.raises(HttpClientError):
            client.request(url="http://example.com", method="GET", data={})

        # Should only try once, no retries
        assert mock_request.call_count == 1

    @patch("httpx.Client.request")
    def test_no_retry_on_connection_error(
        self,
        mock_request: Mock,
        mock_logger: LoggerContract,
    ) -> None:
        """Should not retry on connection errors (HTTPError without status code)."""
        # Arrange
        connection_error = HTTPError("Connection failed")
        mock_request.side_effect = connection_error

        client = BaseHttpClient(logger=mock_logger)

        # Act & Assert
        with pytest.raises(HttpClientError):
            client.request(url="http://example.com", method="GET", data={})

        # Should only try once (HTTPError without status code doesn't retry)
        assert mock_request.call_count == 1


class TestBaseHttpClientEdgeCases:
    """Test edge cases and boundary conditions."""

    @patch("httpx.Client.request")
    def test_request_with_empty_data(
        self,
        mock_request: Mock,
        mock_logger: LoggerContract,
    ) -> None:
        """Should handle empty data dictionary."""
        # Arrange
        mock_response = create_mock_response()
        mock_request.return_value = mock_response

        client = BaseHttpClient(logger=mock_logger)

        # Act
        result = client.request(url="http://example.com", method="POST", data={})

        # Assert
        assert result == mock_response
        mock_request.assert_called_once()

    @patch("httpx.Client.request")
    def test_request_with_none_headers(
        self,
        mock_request: Mock,
        mock_logger: LoggerContract,
    ) -> None:
        """Should handle None headers gracefully."""
        # Arrange
        mock_response = create_mock_response()
        mock_request.return_value = mock_response

        client = BaseHttpClient(logger=mock_logger)

        # Act
        result = client.request(
            url="http://example.com",
            method="GET",
            data={},
            headers=None,
        )

        # Assert
        assert result == mock_response
        call_args = mock_request.call_args
        assert call_args.kwargs["headers"] is None

    @patch("httpx.Client.request")
    def test_request_uses_default_timeout_when_none_provided(
        self,
        mock_request: Mock,
        mock_logger: LoggerContract,
    ) -> None:
        """Should use default timeout when none is provided."""
        # Arrange
        mock_response = create_mock_response()
        mock_request.return_value = mock_response

        client = BaseHttpClient(logger=mock_logger)

        # Act
        client.request(url="http://example.com", method="GET", data={})

        # Assert
        call_args = mock_request.call_args
        assert call_args.kwargs["timeout"] == BaseHttpClient.DEFAULT_TIMEOUT
