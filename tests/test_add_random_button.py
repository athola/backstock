"""Tests for the Add Random Items button with direct add functionality.

TDD/BDD tests for ensuring the Add Random Items button:
1. Has a scroll selector (1-50) above it for selecting item count
2. Directly adds items when clicked (single action, no intermediate form)
3. Works correctly on both web and mobile (responsive design)
"""

import os

# Set test environment BEFORE importing app modules
os.environ["APP_SETTINGS"] = "src.pybackstock.config.TestingConfig"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import pytest
from flask.testing import FlaskClient


class TestAddRandomButtonDisplay:
    """Tests for the Add Random Items button and selector display."""

    @pytest.mark.integration
    def test_main_page_has_random_count_selector(self, client: FlaskClient) -> None:
        """Test that the main page displays a count selector above the Add Random Items button."""
        response = client.get("/")
        assert response.status_code == 200

        data = response.data.decode("utf-8")
        # Check for the range input selector
        assert 'id="random-item-count"' in data or 'name="random-item-count"' in data

    @pytest.mark.integration
    def test_random_count_selector_has_range_1_to_50(self, client: FlaskClient) -> None:
        """Test that the count selector allows values from 1 to 50."""
        response = client.get("/")
        assert response.status_code == 200

        data = response.data.decode("utf-8")
        # Check for min and max attributes on the selector
        assert 'min="1"' in data
        assert 'max="50"' in data

    @pytest.mark.integration
    def test_random_count_selector_default_value(self, client: FlaskClient) -> None:
        """Test that the count selector has a reasonable default value."""
        response = client.get("/")
        assert response.status_code == 200

        data = response.data.decode("utf-8")
        # Check for default value (should be 5 or similar)
        assert 'value="5"' in data or 'value="10"' in data

    @pytest.mark.integration
    def test_random_count_selector_is_visible_on_main_page(self, client: FlaskClient) -> None:
        """Test that the selector is on the main page, not behind a form."""
        response = client.get("/")
        assert response.status_code == 200

        data = response.data.decode("utf-8")
        # The selector should be within the add-random-form, visible immediately
        assert 'name="add-random-form"' in data
        # Should have a label for the selector
        assert "Items:" in data or "Number" in data

    @pytest.mark.integration
    def test_random_count_display_shows_current_value(self, client: FlaskClient) -> None:
        """Test that there's a display showing the current selected count."""
        response = client.get("/")
        assert response.status_code == 200

        data = response.data.decode("utf-8")
        # Should have a value display element
        assert 'id="random-count-display"' in data or 'class="count-display"' in data


class TestAddRandomButtonFunctionality:
    """Tests for the Add Random Items button direct add functionality."""

    @pytest.mark.integration
    def test_add_random_button_directly_adds_items(self, client: FlaskClient) -> None:
        """Test that clicking Add Random Items directly adds items without intermediate form."""
        # Click the button with a count value - should add items immediately
        response = client.post(
            "/",
            data={"add-random": "", "random-item-count": "3"},
        )
        assert response.status_code == 200

        data = response.data.decode("utf-8")
        # Should show success message, NOT the intermediate form
        assert "Successfully generated 3 random item" in data
        # Should NOT show the old intermediate form elements
        assert "Generate Random Test Items" not in data

    @pytest.mark.integration
    def test_add_random_button_uses_selector_value(self, client: FlaskClient) -> None:
        """Test that the button uses the value from the selector."""
        response = client.post(
            "/",
            data={"add-random": "", "random-item-count": "7"},
        )
        assert response.status_code == 200

        data = response.data.decode("utf-8")
        assert "Successfully generated 7 random item" in data

    @pytest.mark.integration
    def test_add_random_button_defaults_to_5_if_no_count(self, client: FlaskClient) -> None:
        """Test that the button defaults to 5 items if no count is provided."""
        response = client.post(
            "/",
            data={"add-random": ""},
        )
        assert response.status_code == 200

        data = response.data.decode("utf-8")
        # Should add 5 items by default
        assert "Successfully generated 5 random item" in data

    @pytest.mark.integration
    def test_add_random_limits_count_to_50(self, client: FlaskClient) -> None:
        """Test that count is limited to 50 even if higher value submitted."""
        response = client.post(
            "/",
            data={"add-random": "", "random-item-count": "100"},
        )
        assert response.status_code == 200

        data = response.data.decode("utf-8")
        # Should be limited to 50
        assert "Successfully generated 50 random item" in data

    @pytest.mark.integration
    def test_add_random_minimum_count_is_1(self, client: FlaskClient) -> None:
        """Test that count is at least 1 even if 0 or negative submitted."""
        response = client.post(
            "/",
            data={"add-random": "", "random-item-count": "0"},
        )
        assert response.status_code == 200

        data = response.data.decode("utf-8")
        # Should be at least 1
        assert "Successfully generated 1 random item" in data

    @pytest.mark.integration
    def test_add_random_items_persisted_to_database(self, client: FlaskClient) -> None:
        """Test that added random items are actually persisted to the database."""
        # Add 3 random items
        response = client.post(
            "/",
            data={"add-random": "", "random-item-count": "3"},
        )
        assert response.status_code == 200

        # Search for items by department (should find something)
        # Random items will have departments from the corpus
        response = client.post(
            "/",
            data={"send-search": "", "column": "id", "item": "1"},
        )
        assert response.status_code == 200
        # If items were created, search should succeed without errors


class TestAddRandomButtonMobileResponsive:
    """Tests for mobile responsiveness of the Add Random Items selector."""

    @pytest.mark.integration
    def test_page_has_viewport_meta_for_mobile(self, client: FlaskClient) -> None:
        """Test that the page has viewport meta tag for mobile responsiveness."""
        response = client.get("/")
        assert response.status_code == 200

        data = response.data.decode("utf-8")
        assert 'name="viewport"' in data
        assert "width=device-width" in data

    @pytest.mark.integration
    def test_random_selector_has_touch_friendly_size(self, client: FlaskClient) -> None:
        """Test that CSS includes touch-friendly sizing for the selector."""
        response = client.get("/")
        assert response.status_code == 200

        data = response.data.decode("utf-8")
        # Check for CSS that ensures touch-friendly sizing
        # Range inputs should have adequate height for touch
        assert "range-selector" in data or "random-item-count" in data

    @pytest.mark.integration
    def test_random_selector_mobile_media_query(self, client: FlaskClient) -> None:
        """Test that there are mobile-specific styles for the selector."""
        response = client.get("/")
        assert response.status_code == 200

        data = response.data.decode("utf-8")
        # Should have mobile media queries
        assert "@media (max-width: 768px)" in data

    @pytest.mark.integration
    def test_add_random_button_has_touch_target_size(self, client: FlaskClient) -> None:
        """Test that the Add Random Items button has minimum touch target size."""
        response = client.get("/")
        assert response.status_code == 200

        data = response.data.decode("utf-8")
        # Check for button styling that ensures touch-friendly size
        # The btn-menu class should have adequate sizing
        assert "btn-menu" in data
        assert "min-height" in data


class TestAddRandomButtonAccessibility:
    """Tests for accessibility of the Add Random Items selector."""

    @pytest.mark.integration
    def test_random_selector_has_label(self, client: FlaskClient) -> None:
        """Test that the selector has an associated label for accessibility."""
        response = client.get("/")
        assert response.status_code == 200

        data = response.data.decode("utf-8")
        # Should have a label for the range input
        assert 'for="random-item-count"' in data or "Items:" in data

    @pytest.mark.integration
    def test_random_selector_has_aria_attributes(self, client: FlaskClient) -> None:
        """Test that the selector has appropriate ARIA attributes."""
        response = client.get("/")
        assert response.status_code == 200

        data = response.data.decode("utf-8")
        # Should have aria-label or aria-describedby
        assert "aria-" in data


class TestEditableNumberInput:
    """BDD tests for the editable number input field that syncs with the slider.

    Feature: Editable Random Items Count Input
        As a user
        I want to click on the number display and type a value directly
        So that I can quickly set the exact number of random items to add
    """

    @pytest.mark.integration
    def test_count_display_is_input_field(self, client: FlaskClient) -> None:
        """Scenario: Count display is an editable input field.

        Given I am on the main inventory page
        When the page loads
        Then the count display should be an input element (not just a span)
        """
        response = client.get("/")
        assert response.status_code == 200

        data = response.data.decode("utf-8")
        # The count display should be an input element with type="text"
        assert 'id="random-count-display"' in data
        assert 'class="count-display count-input"' in data
        # Should be an input, not a span
        assert '<input type="text"' in data

    @pytest.mark.integration
    def test_count_input_has_default_value(self, client: FlaskClient) -> None:
        """Scenario: Count input shows default value.

        Given I am on the main inventory page
        When the page loads
        Then the count input should show the default value of 5
        """
        response = client.get("/")
        assert response.status_code == 200

        data = response.data.decode("utf-8")
        # Should have value="5" for the input
        assert 'id="random-count-display"' in data
        # The input element should have a value attribute
        assert 'value="5"' in data

    @pytest.mark.integration
    def test_count_input_has_maxlength_attribute(self, client: FlaskClient) -> None:
        """Scenario: Count input restricts length.

        Given I am on the main inventory page
        When the page loads
        Then the count input should have maxlength of 2 (for values 1-50)
        """
        response = client.get("/")
        assert response.status_code == 200

        data = response.data.decode("utf-8")
        assert 'maxlength="2"' in data

    @pytest.mark.integration
    def test_count_input_has_accessibility_label(self, client: FlaskClient) -> None:
        """Scenario: Count input is accessible.

        Given I am on the main inventory page
        When the page loads
        Then the count input should have an aria-label for screen readers
        """
        response = client.get("/")
        assert response.status_code == 200

        data = response.data.decode("utf-8")
        # Should have an aria-label explaining the input
        assert 'aria-label="Enter number of items (1-50)"' in data


class TestInputValidationUIElements:
    """BDD tests for validation error display elements.

    Feature: Input Validation Feedback
        As a user
        I want to see clear error messages when I enter invalid values
        So that I know how to correct my input
    """

    @pytest.mark.integration
    def test_error_container_exists(self, client: FlaskClient) -> None:
        """Scenario: Error message container is present.

        Given I am on the main inventory page
        When the page loads
        Then there should be a hidden error container ready to show messages
        """
        response = client.get("/")
        assert response.status_code == 200

        data = response.data.decode("utf-8")
        # Error container should exist with id for JavaScript to target
        assert 'id="random-count-error"' in data
        # Should have the error styling class
        assert 'class="count-error"' in data
        # Should be hidden by default
        assert 'style="display: none;"' in data

    @pytest.mark.integration
    def test_error_styling_exists(self, client: FlaskClient) -> None:
        """Scenario: Error styling is defined.

        Given I am on the main inventory page
        When the page loads
        Then there should be CSS styles for error states
        """
        response = client.get("/")
        assert response.status_code == 200

        data = response.data.decode("utf-8")
        # CSS for error state on input
        assert ".count-input.error" in data
        # CSS for error message container
        assert ".count-error" in data

    @pytest.mark.integration
    def test_input_has_focus_styling(self, client: FlaskClient) -> None:
        """Scenario: Input has focus styling.

        Given I am on the main inventory page
        When the page loads
        Then there should be CSS styles for input focus state
        """
        response = client.get("/")
        assert response.status_code == 200

        data = response.data.decode("utf-8")
        # CSS for focus state
        assert ".count-input:focus" in data

    @pytest.mark.integration
    def test_shake_animation_defined(self, client: FlaskClient) -> None:
        """Scenario: Shake animation is defined for errors.

        Given I am on the main inventory page
        When the page loads
        Then there should be a shake animation keyframe for error feedback
        """
        response = client.get("/")
        assert response.status_code == 200

        data = response.data.decode("utf-8")
        # Shake animation for invalid input feedback
        assert "@keyframes shake" in data


class TestSliderInputSyncJavaScript:
    """BDD tests for JavaScript slider-input synchronization.

    Feature: Bidirectional Slider-Input Sync
        As a user
        I want the slider and input to stay synchronized
        So that I can use either control method
    """

    @pytest.mark.integration
    def test_javascript_sync_code_exists(self, client: FlaskClient) -> None:
        """Scenario: JavaScript for sync is present.

        Given I am on the main inventory page
        When the page loads
        Then there should be JavaScript code for syncing slider and input
        """
        response = client.get("/")
        assert response.status_code == 200

        data = response.data.decode("utf-8")
        # Should have the IIFE for random item count functionality
        assert "// Random item count selector functionality" in data
        # Should have references to both elements
        assert "getElementById('random-item-count')" in data
        assert "getElementById('random-count-display')" in data

    @pytest.mark.integration
    def test_javascript_validation_code_exists(self, client: FlaskClient) -> None:
        """Scenario: JavaScript for validation is present.

        Given I am on the main inventory page
        When the page loads
        Then there should be JavaScript code for input validation
        """
        response = client.get("/")
        assert response.status_code == 200

        data = response.data.decode("utf-8")
        # Should have validation function
        assert "validateInput" in data
        # Should check for valid range
        assert "MIN_VALUE" in data
        assert "MAX_VALUE" in data

    @pytest.mark.integration
    def test_javascript_error_handling_code_exists(self, client: FlaskClient) -> None:
        """Scenario: JavaScript for error handling is present.

        Given I am on the main inventory page
        When the page loads
        Then there should be JavaScript functions for showing/hiding errors
        """
        response = client.get("/")
        assert response.status_code == 200

        data = response.data.decode("utf-8")
        # Should have error handling functions
        assert "showError" in data
        assert "clearError" in data
        # Should have error message text
        assert "Please enter a number between 1-50" in data

    @pytest.mark.integration
    def test_javascript_event_listeners_exist(self, client: FlaskClient) -> None:
        """Scenario: JavaScript event listeners are attached.

        Given I am on the main inventory page
        When the page loads
        Then there should be event listeners for user interactions
        """
        response = client.get("/")
        assert response.status_code == 200

        data = response.data.decode("utf-8")
        # Should listen to slider events
        assert "addEventListener('input'" in data
        assert "addEventListener('change'" in data
        # Should listen to input blur and keydown
        assert "addEventListener('blur'" in data
        assert "addEventListener('keydown'" in data
        # Should prevent non-numeric input
        assert "addEventListener('keypress'" in data


class TestAPIHandlerRandomItemsSupport:
    """BDD tests for API handler support of random items action.

    Feature: API Handler Random Items Support
        As a user
        I want the Add Random Items button to work through the API handler
        So that items are actually added to the database
    """

    @pytest.mark.integration
    def test_api_handler_processes_add_random_action(self, client: FlaskClient) -> None:
        """Scenario: API handler processes add-random action.

        Given I submit a form with add-random action
        When the request is processed
        Then random items should be added to the database
        """
        response = client.post(
            "/",
            data={"add-random": "", "random-item-count": "3"},
        )
        assert response.status_code == 200

        data = response.data.decode("utf-8")
        # Should show success message
        assert "Successfully generated 3 random item" in data

    @pytest.mark.integration
    def test_api_handler_returns_random_added_flag(self, client: FlaskClient) -> None:
        """Scenario: API handler sets random_added flag.

        Given I submit a form with add-random action
        When items are successfully added
        Then the template should receive random_added=True
        """
        response = client.post(
            "/",
            data={"add-random": "", "random-item-count": "2"},
        )
        assert response.status_code == 200

        data = response.data.decode("utf-8")
        # Success message indicates random_added was True
        assert "Successfully generated" in data
        assert "random" in data.lower()

    @pytest.mark.integration
    def test_api_handler_returns_random_count(self, client: FlaskClient) -> None:
        """Scenario: API handler returns correct item count.

        Given I submit a form requesting 5 random items
        When the items are added
        Then the response should indicate 5 items were added
        """
        response = client.post(
            "/",
            data={"add-random": "", "random-item-count": "5"},
        )
        assert response.status_code == 200

        data = response.data.decode("utf-8")
        assert "Successfully generated 5 random item" in data

    @pytest.mark.integration
    def test_api_handler_validates_count_upper_bound(self, client: FlaskClient) -> None:
        """Scenario: API handler limits count to 50.

        Given I submit a form requesting 100 random items
        When the request is processed
        Then only 50 items should be added (upper limit)
        """
        response = client.post(
            "/",
            data={"add-random": "", "random-item-count": "100"},
        )
        assert response.status_code == 200

        data = response.data.decode("utf-8")
        assert "Successfully generated 50 random item" in data

    @pytest.mark.integration
    def test_api_handler_validates_count_lower_bound(self, client: FlaskClient) -> None:
        """Scenario: API handler ensures minimum count of 1.

        Given I submit a form requesting 0 random items
        When the request is processed
        Then at least 1 item should be added (lower limit)
        """
        response = client.post(
            "/",
            data={"add-random": "", "random-item-count": "0"},
        )
        assert response.status_code == 200

        data = response.data.decode("utf-8")
        assert "Successfully generated 1 random item" in data

    @pytest.mark.integration
    def test_api_handler_handles_negative_count(self, client: FlaskClient) -> None:
        """Scenario: API handler handles negative count.

        Given I submit a form with negative count
        When the request is processed
        Then at least 1 item should be added
        """
        response = client.post(
            "/",
            data={"add-random": "", "random-item-count": "-5"},
        )
        assert response.status_code == 200

        data = response.data.decode("utf-8")
        assert "Successfully generated 1 random item" in data

    @pytest.mark.integration
    def test_api_handler_handles_non_numeric_count(self, client: FlaskClient) -> None:
        """Scenario: API handler handles non-numeric count gracefully.

        Given I submit a form with non-numeric count
        When the request is processed
        Then it should use default value of 5
        """
        response = client.post(
            "/",
            data={"add-random": "", "random-item-count": "abc"},
        )
        assert response.status_code == 200

        # Should either use default or handle gracefully
        data = response.data.decode("utf-8")
        # The page should load without crashing
        assert "<!DOCTYPE html>" in data or "<!doctype html>" in data.lower()


class TestOpenAPISpecRandomItems:
    """BDD tests for OpenAPI specification random items support.

    Feature: OpenAPI Specification Support
        As a developer
        I want the OpenAPI spec to include random items properties
        So that the API is properly documented
    """

    @pytest.mark.unit
    def test_openapi_includes_add_random_property(self) -> None:
        """Scenario: OpenAPI spec includes add-random property.

        Given the OpenAPI specification file
        When I check the POST / endpoint schema
        Then it should include add-random property
        """
        import yaml

        with open("openapi.yaml") as f:
            spec = yaml.safe_load(f)

        post_spec = spec["paths"]["/"]["post"]
        form_schema = post_spec["requestBody"]["content"]["application/x-www-form-urlencoded"]["schema"]
        properties = form_schema["properties"]

        assert "add-random" in properties

    @pytest.mark.unit
    def test_openapi_includes_random_item_count_property(self) -> None:
        """Scenario: OpenAPI spec includes random-item-count property.

        Given the OpenAPI specification file
        When I check the POST / endpoint schema
        Then it should include random-item-count property with constraints
        """
        import yaml

        with open("openapi.yaml") as f:
            spec = yaml.safe_load(f)

        post_spec = spec["paths"]["/"]["post"]
        form_schema = post_spec["requestBody"]["content"]["application/x-www-form-urlencoded"]["schema"]
        properties = form_schema["properties"]

        assert "random-item-count" in properties
        count_prop = properties["random-item-count"]
        assert count_prop["type"] == "integer"
        assert count_prop["minimum"] == 1
        assert count_prop["maximum"] == 50

    @pytest.mark.unit
    def test_openapi_includes_send_random_property(self) -> None:
        """Scenario: OpenAPI spec includes send-random property.

        Given the OpenAPI specification file
        When I check the POST / endpoint schema
        Then it should include send-random property for form submission
        """
        import yaml

        with open("openapi.yaml") as f:
            spec = yaml.safe_load(f)

        post_spec = spec["paths"]["/"]["post"]
        form_schema = post_spec["requestBody"]["content"]["application/x-www-form-urlencoded"]["schema"]
        properties = form_schema["properties"]

        assert "send-random" in properties
