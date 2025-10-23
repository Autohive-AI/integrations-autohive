# Asana Integration for Autohive

Connects Autohive to the Asana API to enable task management, project organization, workspace collaboration, and team productivity automation.

## Description

This integration provides a comprehensive connection to Asana's project management platform. It allows users to automate task creation, project management, team collaboration, and workflow automation directly from Autohive.

The integration uses Asana API v1.0 with Personal Access Token authentication and implements 18 comprehensive actions covering tasks, projects, sections, comments, and subtasks.

## Setup & Authentication

This integration uses **Custom Authentication** with Asana Personal Access Token (PAT).

### Authentication Method

Asana uses Bearer token authentication with Personal Access Tokens. The integration handles the authentication automatically by adding your PAT to the Authorization header in all API requests.

### Required Authentication Fields

- **`personal_access_token`**: Your Asana Personal Access Token
  - Created in Asana Settings > Apps > Manage Developer Apps
  - Long-lived token that doesn't expire automatically
  - Acts with same permissions as your Asana account
  - Must be kept secure (treat like a password)

### How to Get Your Personal Access Token

1. **Log in to Asana**: Go to https://app.asana.com
2. **Open Settings**: Click your profile initials in the top right corner
3. **Navigate to Apps**: Select "Settings" from the dropdown menu
4. **Access Developer Apps**: Click on the "Apps" tab
5. **Manage Tokens**: Select "Manage Developer Apps" at the bottom left
6. **Create Token**: Click "+ Create new token"
7. **Save Token**: Name it (e.g., "Autohive Integration"), agree to API terms, click "Create token", and **copy immediately** (shown only once!)

### Setup Steps in Autohive

1. Get your Personal Access Token (follow steps above)
2. Add Asana integration in Autohive
3. Paste your token in the `personal_access_token` field
4. Save configuration

## Actions

### Tasks (5 actions)

#### `create_task`
Creates a new task in Asana.

**Inputs:**
- `name` (required): Task name/title
- `workspace` (optional): Workspace GID (required if projects not provided)
- `projects` (optional): Array of project GIDs to add task to
- `assignee` (optional): User GID or 'me' for current user
- `notes` (optional): Task description (supports rich text)
- `due_on` (optional): Due date (YYYY-MM-DD)
- `due_at` (optional): Due date with time (ISO 8601)
- `completed` (optional): Whether task is completed

**Outputs:**
- `task`: Created task object
- `result`: Success status

---

#### `get_task`
Retrieves details of a specific task by GID.

**Inputs:**
- `task_gid` (required): The GID of the task
- `opt_fields` (optional): Array of fields to include (e.g., ['assignee', 'due_on', 'projects'])

**Outputs:**
- `task`: Task object with details
- `result`: Success status

---

#### `update_task`
Updates an existing task.

**Inputs:**
- `task_gid` (required): The GID of the task to update
- `name` (optional): Updated task name
- `notes` (optional): Updated task notes
- `assignee` (optional): Updated assignee GID, 'me', or null to unassign
- `due_on` (optional): Updated due date (YYYY-MM-DD)
- `due_at` (optional): Updated due date with time
- `completed` (optional): Mark as completed/incomplete

**Outputs:**
- `task`: Updated task object
- `result`: Success status

---

#### `list_tasks`
Returns tasks filtered by project, section, assignee, or workspace.

**Important:** Asana requires at least one filter:
- `project` alone, OR
- `section` alone, OR
- `assignee` + `workspace` together

**Inputs:**
- `project` (optional): Project GID to filter by
- `section` (optional): Section GID to filter by
- `assignee` (optional): Assignee GID or 'me' (requires workspace)
- `workspace` (optional): Workspace GID (requires assignee)
- `completed_since` (optional): Return tasks completed after this time (ISO 8601)
- `limit` (optional): Max tasks to return (max 100)
- `opt_fields` (optional): Array of fields to include

**Outputs:**
- `tasks`: Array of task objects
- `result`: Success status

---

#### `delete_task`
Deletes a task permanently.

**Inputs:**
- `task_gid` (required): The GID of the task to delete

**Outputs:**
- `result`: Success status

---

### Projects (6 actions)

#### `list_projects`
Returns projects in a workspace or team.

**Inputs:**
- `workspace` (optional): Workspace GID to filter by
- `team` (optional): Team GID to filter by
- `archived` (optional): Only return archived projects
- `limit` (optional): Max projects to return (max 100)

**Outputs:**
- `projects`: Array of project objects
- `result`: Success status

---

#### `get_project`
Retrieves details of a specific project by GID.

**Inputs:**
- `project_gid` (required): The GID of the project
- `opt_fields` (optional): Array of fields to include

**Outputs:**
- `project`: Project object with details
- `result`: Success status

---

#### `get_project_by_name`
Get a project by its exact name. This action paginates through all projects to find a match by name.

**Inputs:**
- `name` (required): The exact name of the project to find
- `workspace` (optional): Workspace GID to search in (recommended for better performance)
- `team` (optional): Team GID to search in
- `archived` (optional): Whether to include archived projects in search (default: false)

**Outputs:**
- `gid`: The project GID (null if not found)
- `name`: The project name (null if not found)
- `workspace`: The workspace object (null if not found)
- `team`: The team object (null if not found)
- `archived`: Whether the project is archived (null if not found)
- `color`: Project color (null if not found)
- `notes`: Project notes (null if not found)
- `not_found`: Boolean indicating if project was not found

**Note:** This action iterates through all accessible projects to find a name match. For better performance, provide a `workspace` parameter to narrow the search scope.

---

#### `create_project`
Creates a new project in Asana.

**Inputs:**
- `name` (required): Project name
- `workspace` (required): Workspace GID
- `team` (optional): Team GID (required for organization workspaces)
- `notes` (optional): Project description
- `color` (optional): Project color
- `public` (optional): Whether project is public to workspace

**Outputs:**
- `project`: Created project object
- `result`: Success status

---

#### `update_project`
Updates an existing project's details.

**Inputs:**
- `project_gid` (required): The GID of the project
- `name` (optional): Updated project name
- `notes` (optional): Updated project notes
- `color` (optional): Updated project color
- `public` (optional): Updated public setting
- `archived` (optional): Archive or unarchive project

**Outputs:**
- `project`: Updated project object
- `result`: Success status

---

#### `delete_project`
Deletes a project permanently.

**Inputs:**
- `project_gid` (required): The GID of the project to delete

**Outputs:**
- `result`: Success status

---

### Sections (4 actions)

#### `list_sections`
Returns all sections in a project (columns in board view or headers in list view).

**Inputs:**
- `project_gid` (required): Project GID to get sections from
- `limit` (optional): Max sections to return (max 100)

**Outputs:**
- `sections`: Array of section objects
- `result`: Success status

---

#### `create_section`
Creates a new section in a project.

**Inputs:**
- `project_gid` (required): Project GID to create section in
- `name` (required): Section name

**Outputs:**
- `section`: Created section object
- `result`: Success status

---

#### `update_section`
Updates a section's name.

**Inputs:**
- `section_gid` (required): The GID of the section
- `name` (required): Updated section name

**Outputs:**
- `section`: Updated section object
- `result`: Success status

---

#### `add_task_to_section`
Moves a task to a specific section within a project.

**Inputs:**
- `section_gid` (required): The GID of the section
- `task_gid` (required): The GID of the task to add

**Outputs:**
- `result`: Success status

---

### Comments/Stories (2 actions)

#### `create_story`
Adds a comment (story) to a task.

**Inputs:**
- `task_gid` (required): The GID of the task
- `text` (required): Comment text (plain text or rich text)

**Outputs:**
- `story`: Created story/comment object
- `result`: Success status

---

#### `list_stories`
Gets all comments and stories for a task.

**Inputs:**
- `task_gid` (required): The GID of the task
- `limit` (optional): Max stories to return (max 100)

**Outputs:**
- `stories`: Array of story/comment objects
- `result`: Success status

---

### Subtasks (1 action)

#### `create_subtask`
Creates a subtask under a parent task.

**Inputs:**
- `parent_task_gid` (required): The GID of the parent task
- `name` (required): Subtask name
- `assignee` (optional): Assignee GID or 'me'
- `notes` (optional): Subtask description
- `due_on` (optional): Due date (YYYY-MM-DD)

**Outputs:**
- `subtask`: Created subtask object
- `result`: Success status

---

## Requirements

- `autohive_integrations_sdk` - The Autohive integrations SDK

## API Information

- **API Version**: v1.0
- **Base URL**: `https://app.asana.com/api/1.0`
- **Authentication**: Bearer Token (Personal Access Token)
- **Documentation**: https://developers.asana.com/docs
- **Rate Limits**:
  - Free plan: 150 requests per minute
  - Paid plans: 1,500 requests per minute

## Important Notes

- Personal Access Token provides same access as your Asana account
- Keep your token secure and never share it publicly
- Token will only be shown once when created - copy it immediately
- Can create multiple tokens for different integrations
- Asana wraps all API requests and responses in a `data` object
- GID (Global Identifier) is used for all resource references
- `list_tasks` requires specific filter combinations (see action details)

## Testing

To test the integration:

1. Navigate to the integration directory: `cd asana`
2. Install dependencies: `pip install -r requirements.txt`
3. Update test credentials in `tests/test_asana.py`
4. Run tests: `python tests/test_asana.py`

## Common Use Cases

**Task Automation:**
1. Create tasks from external triggers (emails, forms, etc.)
2. Update task status as work progresses
3. Assign tasks to team members
4. Mark tasks complete when done
5. Create subtasks to break down complex work
6. Delete obsolete tasks

**Project Management:**
1. List all projects in workspace
2. Find projects by name (no need to know GID)
3. Create new projects automatically
4. Update project details and status
5. Archive completed projects
6. Delete unnecessary projects
7. Get project details for reporting

**Section Organization:**
1. Create sections for workflow stages (To Do, In Progress, Done)
2. Move tasks between sections
3. Update section names as workflow evolves
4. List all sections in a project

**Team Communication:**
1. Add comments to tasks for updates
2. View all comments and activity history
3. Track conversation threads
4. Document decisions and discussions

**Workflow Automation:**
1. Create project templates with sections
2. Auto-assign tasks based on rules
3. Move tasks through workflow stages
4. Add status updates as comments
5. Break down epics into subtasks

## Version History

- **1.1.0** - Added name-based lookup capability
  - Projects: Added get_project_by_name action for finding projects by name without needing GID
  - Follows pagination pattern from Slack integration for efficient searching
  - Total actions: 18

- **1.0.0** - Initial release with 17 comprehensive actions
  - Tasks: create, get, update, list, delete (5 actions)
  - Projects: list, get, create, update, delete (5 actions)
  - Sections: list, create, update, add_task_to_section (4 actions)
  - Comments: create_story, list_stories (2 actions)
  - Subtasks: create_subtask (1 action)
