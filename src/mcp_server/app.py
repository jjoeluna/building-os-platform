import os
import json
from flask import Flask, jsonify, request
import requests  # Import the requests library

# --- DEBUGGING BLOCK ---
print("--- STARTING MCP SERVER ---")
print("Attempting to read environment variables...")
api_key = os.getenv("NOTION_API_KEY")
adr_db_id = os.getenv("NOTION_ADR_DATABASE_ID")
print(f"NOTION_API_KEY is present: {isinstance(api_key, str) and len(api_key) > 0}")
print(
    f"NOTION_ADR_DATABASE_ID is present: {isinstance(adr_db_id, str) and len(adr_db_id) > 0}"
)
print("--- FINISHED READING ENV VARS ---")
# --- END OF DEBUGGING BLOCK ---


# Initialize the Flask App
app = Flask(__name__)

# --- Configuration ---
# Load all necessary IDs from environment variables
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
DATABASE_IDS = {
    "adrs": os.getenv("NOTION_ADR_DATABASE_ID"),
    "tasks": os.getenv("NOTION_TASKS_DATABASE_ID"),
    "components": os.getenv("NOTION_COMPONENTS_DATABASE_ID"),
    "lessons": os.getenv("NOTION_LESSONS_DATABASE_ID"),
}
NOTION_API_BASE_URL = "https://api.notion.com/v1"

# --- MCP Manifests ---


@app.route("/.well-known/ai-plugin.json", methods=["GET"])
def get_ai_plugin():
    """Serves the AI Plugin manifest."""
    plugin_info = {
        "schema_version": "v1",
        "name_for_model": "NotionArchitectAssistant",
        "name_for_human": "Notion Architect Assistant",
        "description_for_model": "Plugin for interacting with the BuildingOS Notion workspace. Use it to create and manage documentation pages like Architecture Decision Records (ADRs).",
        "description_for_human": "Interacts with the BuildingOS Notion workspace.",
        "api": {"type": "mcp"},
    }
    return jsonify(plugin_info)


@app.route("/mcp.json", methods=["GET"])
def get_mcp_manifest():
    """Serves the list of available tools (MCP Manifest)."""
    tools = []
    # Dynamically create a tool for each database ID we have
    for db_name, db_id in DATABASE_IDS.items():
        if db_id:  # Only create a tool if the environment variable was set
            tools.append(
                {
                    "id": f"create_page_in_{db_name}",
                    "description": f"Creates a new page in the {db_name.upper()} database in Notion.",
                    "parameters": [
                        {
                            "id": "title",
                            "description": "The title of the new page.",
                            "type": "string",
                            "required": True,
                        }
                    ],
                }
            )
    return jsonify({"tools": tools})


# --- Tool Execution ---


@app.route("/tools/<tool_id>", methods=["POST"])
def execute_tool(tool_id):
    """Executes a specific tool call."""
    print(f"Executing tool: {tool_id}")

    # This dictionary maps the database name to the actual 'Title' property name in Notion
    # This is a crucial detail for the Notion API call.
    title_property_names = {
        "adrs": "Decision Title",
        "tasks": "Task Name",
        "components": "Component Name",
        "lessons": "Lesson Title",
    }

    # Extract the database name from the tool_id (e.g., 'adrs' from 'create_page_in_adrs')
    db_name = tool_id.replace("create_page_in_", "")
    target_database_id = DATABASE_IDS.get(db_name)
    title_property_name = title_property_names.get(db_name)

    if not target_database_id or not title_property_name:
        return (
            jsonify(
                {"error": f"Tool or database '{db_name}' not found or configured."}
            ),
            404,
        )

    # Get the 'title' parameter from the request body
    params = request.get_json()
    page_title = params.get("title")

    if not page_title:
        return jsonify({"error": "Missing 'title' parameter."}), 400

    # --- Call the Notion API ---
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }

    # The payload to create a new page with a title.
    # It now correctly uses the specific title property name for each database.
    payload = {
        "parent": {"database_id": target_database_id},
        "properties": {
            title_property_name: {
                "title": [{"type": "text", "text": {"content": page_title}}]
            }
        },
    }

    try:
        response = requests.post(
            f"{NOTION_API_BASE_URL}/pages", headers=headers, json=payload
        )
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        # Return the result from Notion API
        return jsonify(response.json()), response.status_code

    except Exception as e:
        print(f"Error calling Notion API: {e}")
        return (
            jsonify({"error": "Failed to execute Notion API call.", "details": str(e)}),
            500,
        )


if __name__ == "__main__":
    # This allows the app to be run by App Runner on port 8080
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
