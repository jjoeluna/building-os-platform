import sys
import os
import json

# This is the magic fix:
# We are telling Python to add the project's root directory to the list of places
# it looks for modules. This allows the import of 'src' to work correctly.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.agents.health_check import app  # Now this import will work


def test_health_check_handler():
    """
    Tests that the health check handler returns the expected success response.
    """
    # Call the handler function, passing empty event and context objects
    result = app.handler({}, {})

    # 1. Assert that the status code is 200 (OK)
    assert result["statusCode"] == 200

    # 2. Parse the JSON body of the response
    response_body = json.loads(result["body"])

    # 3. Assert that the content of the body is correct
    assert response_body["status"] == "OK"
    assert "BuildingOS is up and running!" in response_body["message"]
