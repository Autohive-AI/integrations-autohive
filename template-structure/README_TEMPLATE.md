# [Integration Name] Integration for Autohive

<!-- Provide a brief, high-level overview of what this integration does. -->
<!-- Example: Connects Autohive to the [Service Name] API to allow users to [briefly mention key capabilities]. -->

## Description

<!-- Elaborate on the integration's purpose and functionality. -->
<!-- What problems does it solve? What are the main features? -->
<!-- Mention the specific services or APIs it interacts with. -->

## Setup & Authentication

<!-- Explain how users should configure the integration within Autohive. -->
<!-- Detail the authentication method used (e.g., API Key, OAuth2, Basic Auth). -->
<!-- List the required authentication fields (referencing the `config.json`). -->
<!-- Provide step-by-step instructions if the setup is complex (e.g., where to find API keys in the target service). -->

**Authentication Fields:**

*   `field_name_1`: [Description of the field, e.g., Your API Key]
*   `field_name_2`: [Description of the field, e.g., Your User ID]
*   ...

## Actions

<!-- (Optional Section: Include only if your integration has actions) -->
<!-- List and describe actions defined in the `config.json`. -->
<!-- For each action: -->
<!-- - **Action Name:** (e.g., `create_user`) -->
<!-- - **Description:** What does this action do? -->
<!-- - **Inputs:** List the input fields defined in the `input_schema`. -->
<!-- - **Outputs:** Describe the expected output defined in the `output_schema`. -->

### Action: `[action_name_1]`

*   **Description:** [Detailed description of the action]
*   **Inputs:**
    *   `input_field_1`: [Description]
    *   `input_field_2`: [Description]
*   **Outputs:**
    *   `output_field_1`: [Description]
    *   `output_field_2`: [Description]

### Action: `[action_name_2]`

*   **Description:** ...
*   **Inputs:** ...
*   **Outputs:** ...

<!-- Add more actions as needed -->

## Polling Triggers

<!-- (Optional Section: Include only if your integration has polling triggers) -->
<!-- List and describe each polling trigger defined in the `config.json`. -->
<!-- For each trigger: -->
<!-- - **Trigger Name:** (e.g., `new_item_poller`) -->
<!-- - **Description:** What event does this trigger monitor? -->
<!-- - **Polling Interval:** How often does it check for new data? -->
<!-- - **Inputs:** List any configuration inputs for the trigger. -->
<!-- - **Outputs:** Describe the data structure returned when the trigger fires. -->

### Trigger: `[trigger_name_1]`

*   **Description:** [Detailed description of the trigger]
*   **Polling Interval:** [e.g., 5 minutes]
*   **Inputs:**
    *   `input_field_1`: [Description]
*   **Outputs:**
    *   `output_field_1`: [Description]

<!-- Add more triggers as needed -->

## Requirements

<!-- List any external libraries or dependencies required by the integration (from `requirements.txt`). -->
<!-- Mention any specific versions if necessary. -->

*   `library_name_1`
*   `library_name_2>=1.0.0`
*   ...

## Usage Examples

<!-- (Optional but Recommended) -->
<!-- Provide simple examples of how to use the actions or triggers in an Autohive workflow. -->
<!-- This helps users understand the practical application of the integration. -->

**Example 1: [Brief description of the example scenario]**

<!-- Example input for action '[action_name]'
{
  "input_field_1": "value1",
  "input_field_2": "value2"
}

**Example 2: [Brief description of another scenario]**

... -->

## Testing

<!-- Explain how to run the tests included with the integration. -->
<!-- Mention any setup required for testing (e.g., environment variables, mock data). -->

To run the tests:

1.  Navigate to the integration's directory: `cd [integration-directory-name]`
2.  Install dependencies: `pip install -r requirements.txt -t dependencies` (or similar command)
3.  Run the tests: `python tests/test_my_integration.py`
