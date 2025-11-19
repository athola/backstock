# Manual Testing Guide for Report Generation Fix

## Background

The report generation endpoint (`/report`) was failing with a 500 error in production due to Flask app context issues in Connexion 3.x ASGI mode.

## The Fix

Changed `src/pybackstock/api/handlers.py` to import the Flask app instance directly and use `app.app_context()` instead of `current_app.app_context()`.

## Manual Testing Steps

### Local Testing

1. **Start the application locally:**
   ```bash
   uv run python -m src.pybackstock.connexion_app
   ```

2. **Navigate to the report page:**
   Open your browser to `http://localhost:5000/report`

3. **Verify the report loads:**
   - You should see "Inventory Analytics Report" heading
   - Summary metrics should be displayed (Total Items, Total Value, etc.)
   - If the database is empty, you should see "No Inventory Data Available"
   - If there's data, you should see visualizations

4. **Test the JSON API endpoint:**
   ```bash
   curl http://localhost:5000/api/report/data
   ```

   Should return JSON with:
   - `total_items`
   - `total_value`
   - `total_cost`
   - Other summary metrics

### Production Testing (Render.com)

1. **Deploy to Render:**
   Push to the branch and wait for deployment

2. **Test the report endpoint:**
   ```bash
   curl https://your-app.onrender.com/report
   ```

3. **Check for errors:**
   - Status should be 200, not 500
   - Response should contain HTML, not an error JSON

4. **View logs:**
   ```bash
   # Check Render logs for any "Report generation error" messages
   ```

## Expected Behavior

### Success Case
- **Status Code:** 200
- **Response:** HTML page with report visualizations
- **Logs:** No "Report generation error" messages

### Failure Case (Before Fix)
- **Status Code:** 500
- **Response:** `{"type": "about:blank", "title": "Internal Server Error", ...}`
- **Logs:** `RuntimeError: Working outside of application context`

## Integration Test (WIP)

An integration test has been added in `tests/test_connexion_report.py` but requires additional fixture work to properly initialize the database with Connexion ASGI. The test serves as documentation of what should be verified.

### Known Issues with Integration Test
- Database initialization with Connexion's Flask app is complex
- Flask-SQLAlchemy doesn't allow re-initialization of an already configured app
- Test fixtures need refactoring to create a fresh Connexion app for testing

### Future Work
- Refactor test fixtures to create a new connexion app instance for testing
- Or use a different testing approach that doesn't require reconfiguring the existing app
