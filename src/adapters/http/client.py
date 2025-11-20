"""
HTTP Client Adapter

Generic async HTTP client wrapper using httpx
"""
from typing import Dict, Any, Optional
import httpx
from loguru import logger


class HTTPClient:
    """
    Generic async HTTP client wrapper

    Provides common HTTP operations with error handling and logging.
    Use as base for specific API clients or directly for simple requests.

    Example:
        client = HTTPClient(base_url="https://api.example.com")
        response = await client.get("/users/1")
    """

    def __init__(
        self,
        base_url: str = "",
        timeout: float = 30.0,
        headers: Optional[Dict[str, str]] = None
    ):
        """
        Initialize HTTP client

        Args:
            base_url: Base URL for all requests (optional)
            timeout: Default timeout in seconds
            headers: Default headers for all requests
        """
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._default_headers = headers or {}

    def _build_url(self, path: str) -> str:
        """Build full URL from base and path"""
        if path.startswith("http://") or path.startswith("https://"):
            return path
        return f"{self._base_url}/{path.lstrip('/')}"

    def _merge_headers(
        self,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """Merge default headers with request-specific headers"""
        merged = self._default_headers.copy()
        if headers:
            merged.update(headers)
        return merged

    async def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Execute GET request

        Args:
            path: URL path (or full URL)
            params: Query parameters
            headers: Additional headers
            timeout: Request timeout override

        Returns:
            JSON response as dict

        Raises:
            httpx.HTTPError: On HTTP errors
        """
        url = self._build_url(path)
        merged_headers = self._merge_headers(headers)
        request_timeout = timeout or self._timeout

        try:
            async with httpx.AsyncClient(timeout=request_timeout) as client:
                response = await client.get(
                    url,
                    params=params,
                    headers=merged_headers
                )
                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP GET failed: {url} - Status {e.response.status_code}",
                extra={"url": url, "status": e.response.status_code}
            )
            raise
        except httpx.HTTPError as e:
            logger.error(f"HTTP GET error: {url} - {e}")
            raise

    async def post(
        self,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Execute POST request

        Args:
            path: URL path (or full URL)
            data: Form data
            json: JSON body
            headers: Additional headers
            timeout: Request timeout override

        Returns:
            JSON response as dict

        Raises:
            httpx.HTTPError: On HTTP errors
        """
        url = self._build_url(path)
        merged_headers = self._merge_headers(headers)
        request_timeout = timeout or self._timeout

        try:
            async with httpx.AsyncClient(timeout=request_timeout) as client:
                response = await client.post(
                    url,
                    data=data,
                    json=json,
                    headers=merged_headers
                )
                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP POST failed: {url} - Status {e.response.status_code}",
                extra={"url": url, "status": e.response.status_code}
            )
            raise
        except httpx.HTTPError as e:
            logger.error(f"HTTP POST error: {url} - {e}")
            raise

    async def put(
        self,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Execute PUT request

        Args:
            path: URL path (or full URL)
            data: Form data
            json: JSON body
            headers: Additional headers
            timeout: Request timeout override

        Returns:
            JSON response as dict

        Raises:
            httpx.HTTPError: On HTTP errors
        """
        url = self._build_url(path)
        merged_headers = self._merge_headers(headers)
        request_timeout = timeout or self._timeout

        try:
            async with httpx.AsyncClient(timeout=request_timeout) as client:
                response = await client.put(
                    url,
                    data=data,
                    json=json,
                    headers=merged_headers
                )
                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP PUT failed: {url} - Status {e.response.status_code}",
                extra={"url": url, "status": e.response.status_code}
            )
            raise
        except httpx.HTTPError as e:
            logger.error(f"HTTP PUT error: {url} - {e}")
            raise

    async def delete(
        self,
        path: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Execute DELETE request

        Args:
            path: URL path (or full URL)
            headers: Additional headers
            timeout: Request timeout override

        Returns:
            JSON response as dict (or None if no content)

        Raises:
            httpx.HTTPError: On HTTP errors
        """
        url = self._build_url(path)
        merged_headers = self._merge_headers(headers)
        request_timeout = timeout or self._timeout

        try:
            async with httpx.AsyncClient(timeout=request_timeout) as client:
                response = await client.delete(
                    url,
                    headers=merged_headers
                )
                response.raise_for_status()

                # Handle 204 No Content
                if response.status_code == 204:
                    return None
                return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP DELETE failed: {url} - Status {e.response.status_code}",
                extra={"url": url, "status": e.response.status_code}
            )
            raise
        except httpx.HTTPError as e:
            logger.error(f"HTTP DELETE error: {url} - {e}")
            raise

    async def request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Execute generic HTTP request

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, PATCH, etc.)
            path: URL path (or full URL)
            params: Query parameters
            data: Form data
            json: JSON body
            headers: Additional headers
            timeout: Request timeout override

        Returns:
            JSON response as dict (or None if no content)

        Raises:
            httpx.HTTPError: On HTTP errors
        """
        url = self._build_url(path)
        merged_headers = self._merge_headers(headers)
        request_timeout = timeout or self._timeout

        try:
            async with httpx.AsyncClient(timeout=request_timeout) as client:
                response = await client.request(
                    method=method.upper(),
                    url=url,
                    params=params,
                    data=data,
                    json=json,
                    headers=merged_headers
                )
                response.raise_for_status()

                # Handle 204 No Content
                if response.status_code == 204:
                    return None
                return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP {method.upper()} failed: {url} - Status {e.response.status_code}",
                extra={"url": url, "method": method, "status": e.response.status_code}
            )
            raise
        except httpx.HTTPError as e:
            logger.error(f"HTTP {method.upper()} error: {url} - {e}")
            raise
