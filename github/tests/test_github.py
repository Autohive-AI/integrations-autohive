# Testbed for the GitHub integration.
# The IUT (integration under test) is the github.py file
import asyncio
from context import github
from autohive_integrations_sdk import ExecutionContext


async def test_get_user():
    """Test getting authenticated user info"""
    auth = {
        "credentials": {
            "access_token": "your_github_token_here"
        }
    }

    inputs = {}

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await github.execute_action("get_user", inputs, context)
            print(f"Get User Result: {result}")
        except Exception as e:
            print(f"Error testing get_user: {e}")


async def test_list_user_repositories():
    """Test listing repositories for authenticated user"""
    auth = {
        "credentials": {
            "access_token": "your_github_token_here"
        }
    }

    inputs = {
        "type": "all",
        "sort": "updated",
        "direction": "desc"
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await github.execute_action("list_user_repositories", inputs, context)
            print(f"List User Repositories Result: {result}")
        except Exception as e:
            print(f"Error testing list_user_repositories: {e}")


async def test_get_repository():
    """Test getting a specific repository"""
    auth = {
        "credentials": {
            "access_token": "your_github_token_here"
        }
    }

    inputs = {
        "owner": "octocat",
        "repo": "Hello-World"
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await github.execute_action("get_repository", inputs, context)
            print(f"Get Repository Result: {result}")
        except Exception as e:
            print(f"Error testing get_repository: {e}")


async def test_get_issues():
    """Test getting issues for a repository"""
    auth = {
        "credentials": {
            "access_token": "your_github_token_here"
        }
    }

    inputs = {
        "owner": "octocat",
        "repo": "Hello-World",
        "state": "all"
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await github.execute_action("get_issues", inputs, context)
            print(f"Get Issues Result: {result}")
        except Exception as e:
            print(f"Error testing get_issues: {e}")


async def test_get_pull_requests():
    """Test getting pull requests for a repository"""
    auth = {
        "credentials": {
            "access_token": "your_github_token_here"
        }
    }

    inputs = {
        "owner": "octocat",
        "repo": "Hello-World",
        "state": "all"
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await github.execute_action("get_pull_requests", inputs, context)
            print(f"Get Pull Requests Result: {result}")
        except Exception as e:
            print(f"Error testing get_pull_requests: {e}")


async def test_list_branches():
    """Test listing branches for a repository"""
    auth = {
        "credentials": {
            "access_token": "your_github_token_here"
        }
    }

    inputs = {
        "owner": "octocat",
        "repo": "Hello-World"
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await github.execute_action("list_branches", inputs, context)
            print(f"List Branches Result: {result}")
        except Exception as e:
            print(f"Error testing list_branches: {e}")


async def test_get_commits():
    """Test getting commits for a repository"""
    auth = {
        "credentials": {
            "access_token": "your_github_token_here"
        }
    }

    inputs = {
        "owner": "octocat",
        "repo": "Hello-World"
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await github.execute_action("get_commits", inputs, context)
            print(f"Get Commits Result: {result}")
        except Exception as e:
            print(f"Error testing get_commits: {e}")


async def test_get_rate_limit():
    """Test getting rate limit status"""
    auth = {
        "credentials": {
            "access_token": "your_github_token_here"
        }
    }

    inputs = {}

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await github.execute_action("get_rate_limit", inputs, context)
            print(f"Get Rate Limit Result: {result}")
        except Exception as e:
            print(f"Error testing get_rate_limit: {e}")


async def main():
    print("Testing GitHub Integration")
    print("==========================")

    await test_get_user()
    await test_list_user_repositories()
    await test_get_repository()
    await test_get_issues()
    await test_get_pull_requests()
    await test_list_branches()
    await test_get_commits()
    await test_get_rate_limit()


if __name__ == "__main__":
    asyncio.run(main())
