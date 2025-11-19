"""Integration tests for report endpoint using Connexion ASGI.

These tests verify the report generation works correctly when using Connexion 3.x ASGI,
which is how the app runs in production with Gunicorn + Uvicorn workers.

IMPORTANT: These tests use connexion_app.test_client() (Starlette TestClient)
to accurately test the ASGI app context handling that was fixed in the report handlers.
"""

import os
from collections.abc import Generator
from datetime import date
from typing import Any

import pytest

from src.pybackstock import Grocery, db
from src.pybackstock.connexion_app import connexion_app

# Set test environment BEFORE creating fixtures
os.environ["APP_SETTINGS"] = "src.pybackstock.config.TestingConfig"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"


@pytest.fixture()
def connexion_client_with_db() -> Generator[Any, None, None]:
    """Create a Connexion test client with database initialized.

    This fixture properly sets up the database for testing report generation
    in the Connexion ASGI context.

    Yields:
        Starlette TestClient for making requests to the Connexion ASGI app.
    """
    # Get the Flask app from the Connexion app (this is the one db is init'd with)
    flask_app = connexion_app.app

    # Configure for testing - must update BEFORE creating tables
    flask_app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "WTF_CSRF_ENABLED": False,
        }
    )

    # The db is already initialized with flask_app in connexion_app.py
    # Just create tables with the updated config
    with flask_app.app_context():
        # Force the engine to recreate with new URI
        db.engine.dispose()
        db.create_all()

        # Yield the Connexion test client (NOT the Flask test client)
        # This is critical for testing ASGI behavior
        yield connexion_app.test_client()

        # Cleanup
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def sample_inventory_data(connexion_client_with_db: Any) -> None:
    """Add sample inventory items to the database for testing.

    Args:
        connexion_client_with_db: Connexion test client fixture.
    """
    # Use the same Flask app from connexion_app
    flask_app = connexion_app.app

    with flask_app.app_context():
        # Add multiple items to test various report calculations
        items = [
            Grocery(
                item_id=1,
                description="Test Milk",
                last_sold=date(2024, 11, 15),
                shelf_life="7d",
                department="Dairy",
                price="$3.99",
                unit="gal",
                x_for=1,
                cost="$2.50",
                quantity=5,
                reorder_point=10,
                date_added=date(2024, 11, 1),
            ),
            Grocery(
                item_id=2,
                description="Test Bread",
                last_sold=date(2024, 11, 18),
                shelf_life="5d",
                department="Bakery",
                price="$2.49",
                unit="loaf",
                x_for=1,
                cost="$1.25",
                quantity=0,
                reorder_point=5,
                date_added=date(2024, 11, 1),
            ),
            Grocery(
                item_id=3,
                description="Test Apples",
                last_sold=date(2024, 11, 19),
                shelf_life="14d",
                department="Produce",
                price="$4.99",
                unit="lb",
                x_for=1,
                cost="$3.00",
                quantity=25,
                reorder_point=10,
                date_added=date(2024, 10, 15),
            ),
        ]

        for item in items:
            db.session.add(item)
        db.session.commit()


@pytest.mark.integration
class TestReportEndpointASGI:
    """Integration tests for report endpoint with Connexion ASGI."""

    def test_report_endpoint_exists_in_asgi(self, connexion_client_with_db: Any) -> None:
        """Test that /report endpoint is accessible via Connexion ASGI."""
        response = connexion_client_with_db.get("/report")
        # Should not return 404 (endpoint missing)
        assert response.status_code != 404, "Report endpoint should exist in ASGI routing"

    def test_report_with_empty_database(self, connexion_client_with_db: Any) -> None:
        """Test report generation with empty database.

        This verifies that app context handling works correctly even with no data.
        """
        response = connexion_client_with_db.get("/report")
        assert response.status_code == 200, f"Report should handle empty database, got status {response.status_code}"
        assert b"No Inventory Data Available" in response.content

    def test_report_with_sample_data(self, connexion_client_with_db: Any, sample_inventory_data: None) -> None:  # noqa: ARG002
        """Test report generation with sample data.

        This is the critical test that verifies the app context fix works correctly
        in ASGI mode with database queries.
        """
        response = connexion_client_with_db.get("/report")

        # Verify successful response
        assert response.status_code == 200, (
            f"Report generation failed with status {response.status_code}. Response: {response.content[:500]}"
        )

        # Verify report contains expected content
        assert b"Inventory Analytics Report" in response.content, "Report should contain title"

        # Verify some summary metrics are rendered
        content = response.content.decode("utf-8")
        assert "Total Items" in content or "total" in content.lower(), "Report should show total items count"

    def test_report_with_selected_visualizations(
        self, connexion_client_with_db: Any, sample_inventory_data: None  # noqa: ARG002
    ) -> None:
        """Test report with specific visualizations selected."""
        response = connexion_client_with_db.get("/report?viz=stock_health&viz=department")

        assert response.status_code == 200, f"Report with viz params failed: {response.status_code}"
        assert b"Inventory Analytics Report" in response.content

    def test_report_data_api_endpoint(self, connexion_client_with_db: Any, sample_inventory_data: None) -> None:  # noqa: ARG002
        """Test /api/report/data JSON endpoint.

        This endpoint is useful for debugging and verifies JSON serialization works.
        """
        response = connexion_client_with_db.get("/api/report/data")

        assert response.status_code == 200, f"Report data API failed with status {response.status_code}"

        # Verify JSON response
        data = response.json()
        assert data is not None, "Should return valid JSON"
        assert "total_items" in data, "Should include total_items in response"
        assert data["total_items"] == 3, f"Expected 3 items, got {data['total_items']}"

    def test_report_app_context_properly_pushed(
        self, connexion_client_with_db: Any, sample_inventory_data: None  # noqa: ARG002
    ) -> None:
        """Test that Flask app context is properly available for database queries.

        This test specifically validates the fix for the app context issue where
        using current_app.app_context() failed in ASGI mode.
        """
        response = connexion_client_with_db.get("/report")

        # The key assertion: this should NOT return 500 due to app context issues
        assert response.status_code != 500, (
            f"Report should not fail with 500 error due to app context issues. "
            f"Status: {response.status_code}, Response: {response.content[:500]}"
        )

        # Should successfully return rendered HTML
        assert response.status_code == 200, "Report should render successfully"

    def test_report_handles_database_queries_correctly(
        self, connexion_client_with_db: Any, sample_inventory_data: None  # noqa: ARG002
    ) -> None:
        """Test that report can execute database queries within ASGI context.

        This verifies the specific fix where we import the Flask app instance
        directly and use app.app_context() instead of current_app.app_context().
        """
        response = connexion_client_with_db.get("/api/report/data")

        assert response.status_code == 200, "Report data should be accessible"

        data = response.json()
        # Verify data was actually queried from database
        assert data["total_items"] > 0, "Should have queried items from database"
        assert "total_value" in data, "Should have calculated metrics from DB data"
        assert "total_cost" in data, "Should have calculated cost from DB data"

    def test_report_multiple_requests(self, connexion_client_with_db: Any, sample_inventory_data: None) -> None:  # noqa: ARG002
        """Test that report endpoint handles multiple consecutive requests.

        Verifies app context is properly managed across multiple requests.
        """
        responses = []
        for _ in range(5):
            response = connexion_client_with_db.get("/report")
            responses.append(response.status_code)

        # All requests should succeed
        assert all(status == 200 for status in responses), f"All report requests should succeed, got: {responses}"


@pytest.mark.integration
class TestReportCalculationsASGI:
    """Tests for report calculation accuracy in ASGI context."""

    def test_summary_metrics_calculated_correctly(
        self, connexion_client_with_db: Any, sample_inventory_data: None  # noqa: ARG002
    ) -> None:
        """Test that summary metrics are calculated correctly from database."""
        response = connexion_client_with_db.get("/api/report/data")
        data = response.json()

        # Verify expected calculations based on sample data
        assert data["total_items"] == 3, "Should count all items"
        assert data["out_of_stock_count"] >= 1, "Should detect out of stock items"
        assert data["low_stock_count"] >= 1, "Should detect low stock items"

    def test_visualizations_data_present(self, connexion_client_with_db: Any, sample_inventory_data: None) -> None:  # noqa: ARG002
        """Test that visualization data is generated correctly."""
        response = connexion_client_with_db.get("/api/report/data")
        data = response.json()

        # Check that visualization data keys exist
        assert "dept_counts" in data or "department" in str(data), "Should include department visualization data"
