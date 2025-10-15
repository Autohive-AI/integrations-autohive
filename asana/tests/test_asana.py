# Testbed for Asana integration
import asyncio
from context import asana
from autohive_integrations_sdk import ExecutionContext


async def test_list_projects():
    """Test listing projects in workspace."""
    auth = {
        "credentials": {
            "personal_access_token": "your_token_here"
        }
    }

    inputs = {
        "workspace": "your_workspace_gid_here",
        "limit": 10
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await asana.execute_action("list_projects", inputs, context)
            print(f"List Projects Result: {result}")
            return result
        except Exception as e:
            print(f"Error testing list_projects: {e}")
            return None


async def test_get_project():
    """Test getting a specific project."""
    auth = {
        "credentials": {
            "personal_access_token": "your_token_here"
        }
    }

    inputs = {"project_gid": "project_gid_here"}

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await asana.execute_action("get_project", inputs, context)
            print(f"Get Project Result: {result}")
            return result
        except Exception as e:
            print(f"Error testing get_project: {e}")
            return None


async def test_create_task():
    """Test creating a new task."""
    auth = {
        "credentials": {
            "personal_access_token": "your_token_here"
        }
    }

    inputs = {
        "name": "Test Task via Integration",
        "workspace": "your_workspace_gid_here",
        "notes": "This is a test task created via Asana API integration",
        "assignee": "me"
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await asana.execute_action("create_task", inputs, context)
            print(f"Create Task Result: {result}")
            return result
        except Exception as e:
            print(f"Error testing create_task: {e}")
            return None


async def test_get_task():
    """Test getting a specific task."""
    auth = {
        "credentials": {
            "personal_access_token": "your_token_here"
        }
    }

    inputs = {
        "task_gid": "task_gid_here",
        "opt_fields": ["assignee", "due_on", "completed", "projects"]
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await asana.execute_action("get_task", inputs, context)
            print(f"Get Task Result: {result}")
            return result
        except Exception as e:
            print(f"Error testing get_task: {e}")
            return None


async def test_update_task():
    """Test updating a task."""
    auth = {
        "credentials": {
            "personal_access_token": "your_token_here"
        }
    }

    inputs = {
        "task_gid": "task_gid_here",
        "name": "Updated Task Name",
        "completed": True
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await asana.execute_action("update_task", inputs, context)
            print(f"Update Task Result: {result}")
            return result
        except Exception as e:
            print(f"Error testing update_task: {e}")
            return None


async def test_list_tasks():
    """Test listing tasks with filters."""
    auth = {
        "credentials": {
            "personal_access_token": "your_token_here"
        }
    }

    # Filter by assignee + workspace (required combination)
    inputs = {
        "assignee": "me",
        "workspace": "your_workspace_gid_here",
        "limit": 10
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await asana.execute_action("list_tasks", inputs, context)
            print(f"List Tasks Result: {result}")
            return result
        except Exception as e:
            print(f"Error testing list_tasks: {e}")
            return None


async def test_delete_task():
    """Test deleting a task."""
    auth = {
        "credentials": {
            "personal_access_token": "your_token_here"
        }
    }

    inputs = {"task_gid": "task_gid_here"}

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await asana.execute_action("delete_task", inputs, context)
            print(f"Delete Task Result: {result}")
            return result
        except Exception as e:
            print(f"Error testing delete_task: {e}")
            return None


async def test_create_project():
    """Test creating a new project."""
    auth = {"credentials": {"personal_access_token": "your_token_here"}}
    inputs = {
        "name": "Test Project via API",
        "workspace": "your_workspace_gid_here",
        "team": "your_team_gid_here"  # Required for organization workspaces
    }
    async with ExecutionContext(auth=auth) as context:
        try:
            result = await asana.execute_action("create_project", inputs, context)
            print(f"Create Project Result: {result}")
            return result
        except Exception as e:
            print(f"Error testing create_project: {e}")
            return None


async def test_update_project():
    """Test updating a project."""
    auth = {"credentials": {"personal_access_token": "your_token_here"}}
    inputs = {"project_gid": "project_gid_here", "name": "Updated Project Name"}
    async with ExecutionContext(auth=auth) as context:
        try:
            result = await asana.execute_action("update_project", inputs, context)
            print(f"Update Project Result: {result}")
            return result
        except Exception as e:
            print(f"Error testing update_project: {e}")
            return None


async def test_delete_project():
    """Test deleting a project."""
    auth = {"credentials": {"personal_access_token": "your_token_here"}}
    inputs = {"project_gid": "project_gid_here"}
    async with ExecutionContext(auth=auth) as context:
        try:
            result = await asana.execute_action("delete_project", inputs, context)
            print(f"Delete Project Result: {result}")
            return result
        except Exception as e:
            print(f"Error testing delete_project: {e}")
            return None


async def test_list_sections():
    """Test listing sections in a project."""
    auth = {"credentials": {"personal_access_token": "your_token_here"}}
    inputs = {"project_gid": "project_gid_here"}
    async with ExecutionContext(auth=auth) as context:
        try:
            result = await asana.execute_action("list_sections", inputs, context)
            print(f"List Sections Result: {result}")
            return result
        except Exception as e:
            print(f"Error testing list_sections: {e}")
            return None


async def test_create_section():
    """Test creating a section."""
    auth = {"credentials": {"personal_access_token": "your_token_here"}}
    inputs = {"project_gid": "project_gid_here", "name": "To Do"}
    async with ExecutionContext(auth=auth) as context:
        try:
            result = await asana.execute_action("create_section", inputs, context)
            print(f"Create Section Result: {result}")
            return result
        except Exception as e:
            print(f"Error testing create_section: {e}")
            return None


async def test_update_section():
    """Test updating a section."""
    auth = {"credentials": {"personal_access_token": "your_token_here"}}
    inputs = {"section_gid": "section_gid_here", "name": "In Progress"}
    async with ExecutionContext(auth=auth) as context:
        try:
            result = await asana.execute_action("update_section", inputs, context)
            print(f"Update Section Result: {result}")
            return result
        except Exception as e:
            print(f"Error testing update_section: {e}")
            return None


async def test_add_task_to_section():
    """Test adding task to section."""
    auth = {"credentials": {"personal_access_token": "your_token_here"}}
    inputs = {"section_gid": "section_gid_here", "task_gid": "task_gid_here"}
    async with ExecutionContext(auth=auth) as context:
        try:
            result = await asana.execute_action("add_task_to_section", inputs, context)
            print(f"Add Task to Section Result: {result}")
            return result
        except Exception as e:
            print(f"Error testing add_task_to_section: {e}")
            return None


async def test_create_story():
    """Test creating a comment."""
    auth = {"credentials": {"personal_access_token": "your_token_here"}}
    inputs = {"task_gid": "task_gid_here", "text": "This is a test comment"}
    async with ExecutionContext(auth=auth) as context:
        try:
            result = await asana.execute_action("create_story", inputs, context)
            print(f"Create Story Result: {result}")
            return result
        except Exception as e:
            print(f"Error testing create_story: {e}")
            return None


async def test_list_stories():
    """Test listing stories/comments."""
    auth = {"credentials": {"personal_access_token": "your_token_here"}}
    inputs = {"task_gid": "task_gid_here"}
    async with ExecutionContext(auth=auth) as context:
        try:
            result = await asana.execute_action("list_stories", inputs, context)
            print(f"List Stories Result: {result}")
            return result
        except Exception as e:
            print(f"Error testing list_stories: {e}")
            return None


async def test_create_subtask():
    """Test creating a subtask."""
    auth = {"credentials": {"personal_access_token": "your_token_here"}}
    inputs = {"parent_task_gid": "task_gid_here", "name": "Subtask 1"}
    async with ExecutionContext(auth=auth) as context:
        try:
            result = await asana.execute_action("create_subtask", inputs, context)
            print(f"Create Subtask Result: {result}")
            return result
        except Exception as e:
            print(f"Error testing create_subtask: {e}")
            return None


async def main():
    print("Testing Asana Integration - 17 Actions")
    print("=" * 60)
    print()
    print("NOTE: Replace placeholders with actual values:")
    print("  - your_token_here: Your Personal Access Token")
    print("  - your_workspace_gid_here: Your workspace GID")
    print("  - your_team_gid_here: Your team GID")
    print("  - project_gid_here, task_gid_here, section_gid_here")
    print()
    print("To get GIDs:")
    print("  Workspaces: https://app.asana.com/api/1.0/workspaces")
    print("  Teams: https://app.asana.com/api/1.0/organizations/{workspace_gid}/teams")
    print()
    print("=" * 60)
    print()

    # Test project actions (5)
    print("1. Testing list_projects...")
    await test_list_projects()
    print()

    print("2. Testing get_project...")
    await test_get_project()
    print()

    print("3. Testing create_project...")
    await test_create_project()
    print()

    print("4. Testing update_project...")
    await test_update_project()
    print()

    print("5. Testing delete_project...")
    await test_delete_project()
    print()

    # Test task actions (5)
    print("6. Testing create_task...")
    await test_create_task()
    print()

    print("7. Testing get_task...")
    await test_get_task()
    print()

    print("8. Testing update_task...")
    await test_update_task()
    print()

    print("9. Testing list_tasks...")
    await test_list_tasks()
    print()

    print("10. Testing delete_task...")
    await test_delete_task()
    print()

    # Test section actions (4)
    print("11. Testing list_sections...")
    await test_list_sections()
    print()

    print("12. Testing create_section...")
    await test_create_section()
    print()

    print("13. Testing update_section...")
    await test_update_section()
    print()

    print("14. Testing add_task_to_section...")
    await test_add_task_to_section()
    print()

    # Test comment actions (2)
    print("15. Testing create_story...")
    await test_create_story()
    print()

    print("16. Testing list_stories...")
    await test_list_stories()
    print()

    # Test subtask action (1)
    print("17. Testing create_subtask...")
    await test_create_subtask()
    print()

    print("=" * 60)
    print("Testing completed - 17 actions total!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
