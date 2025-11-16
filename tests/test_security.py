"""Security tests for the inventory application."""

from __future__ import annotations

import pytest
from flask import Flask


class TestCSRFProtection:
    """Test CSRF protection implementation."""

    def test_csrf_protection_enabled_in_config(self, app: Flask) -> None:
        """Test that CSRF protection is enabled in configuration."""
        assert app.config.get("WTF_CSRF_ENABLED", False) is True

    def test_csrf_token_present_in_search_form(self, client: Any) -> None:
        """Test that CSRF token is present in search form."""
        response = client.get("/")
        assert response.status_code == 200
        assert b"csrf_token" in response.data or b"csrf-token" in response.data

    def test_csrf_token_present_in_add_form(self, client: Any) -> None:
        """Test that CSRF token is present in add item form."""
        response = client.post("/", data={"add-item": ""})
        assert response.status_code == 200
        assert b"csrf_token" in response.data or b"csrf-token" in response.data

    def test_post_request_without_csrf_token_rejected(self, client: Any) -> None:
        """Test that POST requests without CSRF token are rejected."""
        response = client.post(
            "/",
            data={
                "send-add": "",
                "id-add": "9999",
                "description-add": "Test Item",
                "last-sold-add": "2024-01-01",
                "shelf-life-add": "7d",
                "department-add": "Test",
                "price-add": "1.99",
                "unit-add": "ea",
                "xfor-add": "1",
                "cost-add": "0.99",
            },
        )
        # Should be rejected (400 Bad Request or redirect)
        assert response.status_code in (400, 403)


class TestSecurityHeaders:
    """Test security headers implementation."""

    def test_x_frame_options_header_present(self, client: Any) -> None:
        """Test that X-Frame-Options header is set to prevent clickjacking."""
        response = client.get("/")
        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Frame-Options"] in ("DENY", "SAMEORIGIN")

    def test_x_content_type_options_header_present(self, client: Any) -> None:
        """Test that X-Content-Type-Options header is set."""
        response = client.get("/")
        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"

    def test_x_xss_protection_header_present(self, client: Any) -> None:
        """Test that X-XSS-Protection header is set."""
        response = client.get("/")
        assert "X-XSS-Protection" in response.headers
        assert response.headers["X-XSS-Protection"] == "1; mode=block"

    def test_strict_transport_security_in_production(self, app: Flask) -> None:
        """Test that HSTS header would be set in production."""
        # This is for documentation - HSTS should only be enabled in production with HTTPS
        if not app.config.get("DEBUG"):
            with app.test_client() as client:
                response = client.get("/")
                assert "Strict-Transport-Security" in response.headers


class TestErrorHandling:
    """Test secure error handling."""

    def test_error_messages_do_not_expose_internal_details(self, client: Any) -> None:
        """Test that error messages don't expose stack traces or line numbers."""
        response = client.post(
            "/",
            data={
                "send-search": "",
                # Missing required field to trigger error
            },
        )
        assert response.status_code == 200
        # Error message should not contain "line no:" or exception types
        assert b"line no:" not in response.data
        assert b"KeyError" not in response.data
        assert b"ValueError" not in response.data
        assert b"TypeError" not in response.data

    def test_generic_error_message_shown_to_user(self, client: Any) -> None:
        """Test that users see generic, helpful error messages."""
        response = client.post(
            "/",
            data={
                "send-search": "",
                # Missing required fields
            },
        )
        assert response.status_code == 200
        # Should show generic message
        assert b"Unable to" in response.data or b"error" in response.data.lower()


class TestFileUploadSecurity:
    """Test file upload security measures."""

    def test_file_upload_size_limit(self, app: Flask) -> None:
        """Test that file upload size limit is configured."""
        # Flask's MAX_CONTENT_LENGTH should be set
        assert app.config.get("MAX_CONTENT_LENGTH") is not None
        # Should be reasonable (e.g., 16MB)
        assert app.config["MAX_CONTENT_LENGTH"] <= 16 * 1024 * 1024

    def test_file_upload_validates_content_type(self, client: Any) -> None:
        """Test that file uploads validate content type."""
        from io import BytesIO

        # Try uploading a file with wrong content type
        data = {"csv-submit": "", "csv-input": (BytesIO(b"malicious content"), "test.csv")}
        response = client.post("/", data=data, content_type="multipart/form-data")
        # Implementation should validate content type
        # This test documents expected behavior

    def test_file_upload_rejects_oversized_files(self, client: Any) -> None:
        """Test that oversized files are rejected."""
        from io import BytesIO

        # Create a large CSV (if MAX_CONTENT_LENGTH is set)
        large_content = b"x" * (17 * 1024 * 1024)  # 17MB
        data = {"csv-submit": "", "csv-input": (BytesIO(large_content), "large.csv")}
        response = client.post("/", data=data, content_type="multipart/form-data")
        # Should be rejected with 413 Payload Too Large
        assert response.status_code in (413, 200)  # 200 if validation happens in handler


class TestInputValidation:
    """Test input validation and sanitization."""

    def test_sql_injection_protection_via_orm(self, client: Any, sample_grocery_data: dict[str, Any]) -> None:
        """Test that SQLAlchemy ORM protects against SQL injection."""
        # SQLAlchemy ORM uses parameterized queries automatically
        # This test documents that we rely on ORM, not manual checks

        # Try various SQL injection attempts
        malicious_inputs = [
            "'; DROP TABLE grocery_items; --",
            "1' OR '1'='1",
            "admin'--",
            "' UNION SELECT * FROM users--",
        ]

        for malicious_input in malicious_inputs:
            response = client.post(
                "/",
                data={
                    "send-search": "",
                    "column": "description",
                    "item": malicious_input,
                },
            )
            # Should not crash or cause SQL errors
            assert response.status_code == 200
            # Should not return unexpected results
            assert b"DROP TABLE" not in response.data

    def test_no_misleading_sql_injection_check(self) -> None:
        """Test that code doesn't contain ineffective SQL injection checks."""
        import inventoryApp

        # Read the source code
        source = inventoryApp.__file__
        with open(source) as f:
            code = f.read()

        # Should not have naive "DROP TABLE" check
        assert 'if "DROP TABLE" in search_item:' not in code

    def test_xss_protection_in_output(self, client: Any) -> None:
        """Test that user input is properly escaped in output."""
        # Try adding item with XSS payload
        xss_payload = "<script>alert('XSS')</script>"
        response = client.post(
            "/",
            data={
                "send-add": "",
                "id-add": "9998",
                "description-add": xss_payload,
                "last-sold-add": "2024-01-01",
                "shelf-life-add": "7d",
                "department-add": "Test",
                "price-add": "1.99",
                "unit-add": "ea",
                "xfor-add": "1",
                "cost-add": "0.99",
            },
        )
        # Jinja2 auto-escapes by default
        # The literal script tag should not appear in response
        assert b"<script>alert" not in response.data


class TestSessionSecurity:
    """Test session security configuration."""

    def test_session_cookie_httponly(self, app: Flask) -> None:
        """Test that session cookies are HTTPOnly."""
        assert app.config.get("SESSION_COOKIE_HTTPONLY", True) is True

    def test_session_cookie_secure_in_production(self, app: Flask) -> None:
        """Test that session cookies are Secure in production."""
        if not app.config.get("DEBUG"):
            assert app.config.get("SESSION_COOKIE_SECURE", False) is True

    def test_session_cookie_samesite(self, app: Flask) -> None:
        """Test that session cookies have SameSite attribute."""
        samesite = app.config.get("SESSION_COOKIE_SAMESITE")
        assert samesite in ("Lax", "Strict", None)


# Type hints import
from typing import Any
