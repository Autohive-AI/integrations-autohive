from autohive_integrations_sdk import Integration, ExecutionContext, ActionHandler 
from typing import Dict, Any, List
from datetime import datetime, timedelta

github = Integration.load()

class GitHubAPI:
    """Helper class for GitHub API operations"""
    BASE_URL = "https://api.github.com"

    @staticmethod
    async def get_commits(context: ExecutionContext, owner: str, repo: str, since: str, until: str = None) -> List[Dict[str, Any]]:
        url = f"{GitHubAPI.BASE_URL}/repos/{owner}/{repo}/commits"
        params = {
            'since': since,
            'per_page': 100,  # Maximum allowed by GitHub API
            'page': 1
        }
        if until:
            params['until'] = until

        all_commits = []
        while True:
            commits = await context.fetch(url, params=params)
            if not commits:
                break
                
            all_commits.extend(commits)
            
            # Check if we got less than per_page items, meaning this is the last page
            if len(commits) < params['per_page']:
                break
                
            params['page'] += 1

        return all_commits

    @staticmethod
    async def get_pull_requests(context: ExecutionContext, owner: str, repo: str, state: str = 'all', sort: str = 'updated') -> List[Dict[str, Any]]:
        url = f"{GitHubAPI.BASE_URL}/repos/{owner}/{repo}/pulls"
        params = {
            'state': state,
            'sort': sort,
            'direction': 'desc'
        }
        return await context.fetch(url, params=params)

    @staticmethod
    async def get_repository(context: ExecutionContext, owner: str, repo: str) -> Dict[str, Any]:
        url = f"{GitHubAPI.BASE_URL}/repos/{owner}/{repo}"
        return await context.fetch(url)

    @staticmethod
    async def get_issues(context: ExecutionContext, owner: str, repo: str, state: str = 'all', 
                         sort: str = 'created', direction: str = 'desc', since: str = None) -> List[Dict[str, Any]]:
        """Get issues for a repository with various filters"""
        url = f"{GitHubAPI.BASE_URL}/repos/{owner}/{repo}/issues"
        params = {
            'state': state,
            'sort': sort,
            'direction': direction,
            'per_page': 100,
            'page': 1
        }
        if since:
            params['since'] = since
            
        all_issues = []
        while True:
            issues = await context.fetch(url, params=params)
            if not issues:
                break
                
            all_issues.extend(issues)
            
            # Check if we got less than per_page items, meaning this is the last page
            if len(issues) < params['per_page']:
                break
                
            params['page'] += 1
            
        return all_issues
    
    @staticmethod
    async def create_issue(context: ExecutionContext, owner: str, repo: str, title: str, 
                          body: str = None, assignees: List[str] = None, 
                          labels: List[str] = None, milestone: int = None) -> Dict[str, Any]:
        """Create a new issue in a repository"""
        url = f"{GitHubAPI.BASE_URL}/repos/{owner}/{repo}/issues"
        data = {
            'title': title
        }
        
        if body:
            data['body'] = body
        if assignees:
            data['assignees'] = assignees
        if labels:
            data['labels'] = labels
        if milestone:
            data['milestone'] = milestone
            
        return await context.fetch(url, method="POST", json=data)
    
    @staticmethod
    async def update_issue(context: ExecutionContext, owner: str, repo: str, issue_number: int,
                          title: str = None, body: str = None, state: str = None,
                          assignees: List[str] = None, labels: List[str] = None, 
                          milestone: int = None) -> Dict[str, Any]:
        """Update an existing issue in a repository"""
        url = f"{GitHubAPI.BASE_URL}/repos/{owner}/{repo}/issues/{issue_number}"
        data = {}
        
        if title:
            data['title'] = title
        if body:
            data['body'] = body
        if state:
            data['state'] = state
        if assignees:
            data['assignees'] = assignees
        if labels:
            data['labels'] = labels
        if milestone is not None:  # Can be 0 to clear the milestone
            data['milestone'] = milestone
            
        return await context.fetch(url, method="PATCH", json=data)
    
    @staticmethod
    async def get_issue_comments(context: ExecutionContext, owner: str, repo: str, 
                                issue_number: int) -> List[Dict[str, Any]]:
        """Get comments for an issue"""
        url = f"{GitHubAPI.BASE_URL}/repos/{owner}/{repo}/issues/{issue_number}/comments"
        params = {
            'per_page': 100,
            'page': 1
        }
        
        all_comments = []
        while True:
            comments = await context.fetch(url, params=params)
            if not comments:
                break
                
            all_comments.extend(comments)
            
            # Check if we got less than per_page items, meaning this is the last page
            if len(comments) < params['per_page']:
                break
                
            params['page'] += 1
            
        return all_comments

    @staticmethod
    async def get_pull_request(context: ExecutionContext, owner: str, repo: str, pull_number: int) -> Dict[str, Any]:
        """Get detailed information about a specific pull request"""
        url = f"{GitHubAPI.BASE_URL}/repos/{owner}/{repo}/pulls/{pull_number}"
        return await context.fetch(url)
    
    @staticmethod
    async def merge_pull_request(context: ExecutionContext, owner: str, repo: str, pull_number: int, 
                                commit_title: str = None, commit_message: str = None, 
                                merge_method: str = 'merge') -> Dict[str, Any]:
        """Merge a pull request"""
        url = f"{GitHubAPI.BASE_URL}/repos/{owner}/{repo}/pulls/{pull_number}/merge"
        data = {
            'merge_method': merge_method
        }
        
        if commit_title:
            data['commit_title'] = commit_title
        if commit_message:
            data['commit_message'] = commit_message
            
        return await context.fetch(url, method="PUT", json=data)
    
    @staticmethod
    async def create_pull_request_review(context: ExecutionContext, owner: str, repo: str, pull_number: int,
                                        body: str = None, event: str = None, 
                                        comments: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a review for a pull request"""
        url = f"{GitHubAPI.BASE_URL}/repos/{owner}/{repo}/pulls/{pull_number}/reviews"
        data = {}
        
        if body:
            data['body'] = body
        if event:
            data['event'] = event
        if comments:
            data['comments'] = comments
            
        return await context.fetch(url, method="POST", json=data)

    @staticmethod
    async def create_repository(context: ExecutionContext, name: str, description: str = None, 
                               private: bool = False, auto_init: bool = False, 
                               gitignore_template: str = None, license_template: str = None,
                               org: str = None) -> Dict[str, Any]:
        """Create a new repository"""
        if org:
            url = f"{GitHubAPI.BASE_URL}/orgs/{org}/repos"
        else:
            url = f"{GitHubAPI.BASE_URL}/user/repos"
            
        data = {
            'name': name,
            'private': private,
            'auto_init': auto_init
        }
        
        if description:
            data['description'] = description
        if gitignore_template:
            data['gitignore_template'] = gitignore_template
        if license_template:
            data['license_template'] = license_template
            
        return await context.fetch(url, method="POST", json=data)
    
    @staticmethod
    async def list_branches(context: ExecutionContext, owner: str, repo: str) -> List[Dict[str, Any]]:
        """List branches for a repository"""
        url = f"{GitHubAPI.BASE_URL}/repos/{owner}/{repo}/branches"
        params = {
            'per_page': 100,
            'page': 1
        }
        
        all_branches = []
        while True:
            branches = await context.fetch(url, params=params)
            if not branches:
                break
                
            all_branches.extend(branches)
            
            # Check if we got less than per_page items, meaning this is the last page
            if len(branches) < params['per_page']:
                break
                
            params['page'] += 1
            
        return all_branches
    
    @staticmethod
    async def get_branch_protection(context: ExecutionContext, owner: str, repo: str, branch: str) -> Dict[str, Any]:
        """Get branch protection rules"""
        url = f"{GitHubAPI.BASE_URL}/repos/{owner}/{repo}/branches/{branch}/protection"
        return await context.fetch(url)

    @staticmethod
    async def get_user(context: ExecutionContext, username: str) -> Dict[str, Any]:
        """Get information about a user"""
        url = f"{GitHubAPI.BASE_URL}/users/{username}"
        return await context.fetch(url)
    
    @staticmethod
    async def list_user_repositories(context: ExecutionContext, username: str, 
                                    type: str = 'owner', sort: str = 'updated', 
                                    direction: str = 'desc') -> List[Dict[str, Any]]:
        """List repositories for a user"""
        url = f"{GitHubAPI.BASE_URL}/users/{username}/repos"
        params = {
            'type': type,
            'sort': sort,
            'direction': direction,
            'per_page': 100,
            'page': 1
        }
        
        all_repos = []
        while True:
            repos = await context.fetch(url, params=params)
            if not repos:
                break
                
            all_repos.extend(repos)
            
            # Check if we got less than per_page items, meaning this is the last page
            if len(repos) < params['per_page']:
                break
                
            params['page'] += 1
            
        return all_repos
    
    @staticmethod
    async def list_organization_repositories(context: ExecutionContext, org: str, 
                                           type: str = 'all') -> List[Dict[str, Any]]:
        """List repositories for an organization"""
        url = f"{GitHubAPI.BASE_URL}/orgs/{org}/repos"
        params = {
            'type': type,
            'per_page': 100,
            'page': 1
        }
        
        all_repos = []
        while True:
            repos = await context.fetch(url, params=params)
            if not repos:
                break
                
            all_repos.extend(repos)
            
            # Check if we got less than per_page items, meaning this is the last page
            if len(repos) < params['per_page']:
                break
                
            params['page'] += 1
            
        return all_repos
    
    @staticmethod
    async def list_organization_members(context: ExecutionContext, org: str, 
                                       role: str = 'all') -> List[Dict[str, Any]]:
        """List members of an organization"""
        url = f"{GitHubAPI.BASE_URL}/orgs/{org}/members"
        params = {
            'role': role,
            'per_page': 100,
            'page': 1
        }
        
        all_members = []
        while True:
            members = await context.fetch(url, params=params)
            if not members:
                break
                
            all_members.extend(members)
            
            # Check if we got less than per_page items, meaning this is the last page
            if len(members) < params['per_page']:
                break
                
            params['page'] += 1
            
        return all_members

    @staticmethod
    async def list_workflows(context: ExecutionContext, owner: str, repo: str) -> List[Dict[str, Any]]:
        """List GitHub Actions workflows for a repository"""
        url = f"{GitHubAPI.BASE_URL}/repos/{owner}/{repo}/actions/workflows"
        response = await context.fetch(url)
        return response.get('workflows', [])
    
    @staticmethod
    async def get_workflow_runs(context: ExecutionContext, owner: str, repo: str, 
                               workflow_id: str, status: str = None, 
                               branch: str = None) -> List[Dict[str, Any]]:
        """Get runs for a workflow"""
        url = f"{GitHubAPI.BASE_URL}/repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs"
        params = {
            'per_page': 100,
            'page': 1
        }
        
        if status:
            params['status'] = status
        if branch:
            params['branch'] = branch
            
        all_runs = []
        while True:
            response = await context.fetch(url, params=params)
            runs = response.get('workflow_runs', [])
            
            if not runs:
                break
                
            all_runs.extend(runs)
            
            # Check if we got less than per_page items, meaning this is the last page
            if len(runs) < params['per_page']:
                break
                
            params['page'] += 1
            
        return all_runs

    @staticmethod
    async def create_branch(context: ExecutionContext, owner: str, repo: str, branch_name: str, sha: str) -> Dict[str, Any]:
        """Create a new branch in a repository"""
        # First get the reference to create branch from
        url = f"{GitHubAPI.BASE_URL}/repos/{owner}/{repo}/git/refs"
        data = {
            'ref': f'refs/heads/{branch_name}',
            'sha': sha
        }
        
        return await context.fetch(url, method="POST", json=data)

    @staticmethod
    async def create_pull_request(context: ExecutionContext, owner: str, repo: str, title: str,
                                head: str, base: str, body: str = None, draft: bool = False,
                                maintainer_can_modify: bool = True) -> Dict[str, Any]:
        """Create a new pull request"""
        url = f"{GitHubAPI.BASE_URL}/repos/{owner}/{repo}/pulls"
        data = {
            'title': title,
            'head': head,
            'base': base,
            'draft': draft,
            'maintainer_can_modify': maintainer_can_modify
        }
        
        if body:
            data['body'] = body
            
        return await context.fetch(url, method="POST", json=data)

    @staticmethod
    async def compare_branches(context: ExecutionContext, owner: str, repo: str, base: str, head: str) -> Dict[str, Any]:
        """Compare two branches"""
        url = f"{GitHubAPI.BASE_URL}/repos/{owner}/{repo}/compare/{base}...{head}"
        return await context.fetch(url)

@github.action("list_commits")
class ListCommits(ActionHandler):
    """
    Action that lists commits for a repository within a time range.
    """
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        owner = inputs['owner']
        repo = inputs['repo']
        since = inputs['since']
        until = inputs.get('until')

        commits = await GitHubAPI.get_commits(context, owner, repo, since, until)
        
        # Transform the response to include relevant information
        return [{
            'sha': commit['sha'],
            'author': {
                'name': commit['commit']['author']['name'],
                'email': commit['commit']['author']['email'],
                'date': commit['commit']['author']['date']
            },
            'message': commit['commit']['message'],
            'url': commit['html_url']
        } for commit in commits]

@github.action("list_pull_requests")
class ListPullRequests(ActionHandler):
    """
    Action that lists pull requests for a repository with various filters.
    """
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        owner = inputs['owner']
        repo = inputs['repo']
        state = inputs.get('state', 'all')
        sort = inputs.get('sort', 'updated')

        prs = await GitHubAPI.get_pull_requests(context, owner, repo, state, sort)
        
        # Transform the response to include relevant information
        return [{
            'number': pr['number'],
            'title': pr['title'],
            'description': pr['body'],
            'state': pr['state'],
            'created_at': pr['created_at'],
            'updated_at': pr['updated_at'],
            'merged_at': pr['merged_at'],
            'author': {
                'login': pr['user']['login'],
                'avatar_url': pr['user']['avatar_url']
            },
            'url': pr['html_url']
        } for pr in prs]

@github.action("get_repository")
class GetRepository(ActionHandler):
    """
    Action that retrieves detailed information about a repository.
    """
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        owner = inputs['owner']
        repo = inputs['repo']

        repo_data = await GitHubAPI.get_repository(context, owner, repo)
        
        # Transform the response to include relevant information
        return {
            'name': repo_data['name'],
            'full_name': repo_data['full_name'],
            'description': repo_data['description'],
            'default_branch': repo_data['default_branch'],
            'created_at': repo_data['created_at'],
            'updated_at': repo_data['updated_at'],
            'pushed_at': repo_data['pushed_at'],
            'language': repo_data['language'],
            'visibility': repo_data['visibility'],
            'url': repo_data['html_url']
        }

@github.action("list_issues")
class ListIssues(ActionHandler):
    """
    Action that lists issues for a repository with various filters.
    """
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        owner = inputs['owner']
        repo = inputs['repo']
        state = inputs.get('state', 'all')
        sort = inputs.get('sort', 'created')
        direction = inputs.get('direction', 'desc')
        since = inputs.get('since')
        
        issues = await GitHubAPI.get_issues(context, owner, repo, state, sort, direction, since)
        
        # Transform the response to include relevant information
        return [{
            'number': issue['number'],
            'title': issue['title'],
            'description': issue['body'],
            'state': issue['state'],
            'created_at': issue['created_at'],
            'updated_at': issue['updated_at'],
            'closed_at': issue['closed_at'],
            'author': {
                'login': issue['user']['login'],
                'avatar_url': issue['user']['avatar_url']
            },
            'assignees': [{'login': assignee['login']} for assignee in issue.get('assignees', [])],
            'labels': [{'name': label['name'], 'color': label['color']} for label in issue.get('labels', [])],
            'url': issue['html_url']
        } for issue in issues]

@github.action("create_issue")
class CreateIssue(ActionHandler):
    """
    Action that creates a new issue in a repository.
    """
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        owner = inputs['owner']
        repo = inputs['repo']
        title = inputs['title']
        body = inputs.get('body')
        assignees = inputs.get('assignees')
        labels = inputs.get('labels')
        milestone = inputs.get('milestone')
        
        issue = await GitHubAPI.create_issue(context, owner, repo, title, body, assignees, labels, milestone)
        
        # Transform the response to include relevant information
        return {
            'number': issue['number'],
            'title': issue['title'],
            'description': issue['body'],
            'state': issue['state'],
            'created_at': issue['created_at'],
            'updated_at': issue['updated_at'],
            'author': {
                'login': issue['user']['login'],
                'avatar_url': issue['user']['avatar_url']
            },
            'assignees': [{'login': assignee['login']} for assignee in issue.get('assignees', [])],
            'labels': [{'name': label['name'], 'color': label['color']} for label in issue.get('labels', [])],
            'url': issue['html_url']
        }

@github.action("update_issue")
class UpdateIssue(ActionHandler):
    """
    Action that updates an existing issue in a repository.
    """
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        owner = inputs['owner']
        repo = inputs['repo']
        issue_number = inputs['issue_number']
        title = inputs.get('title')
        body = inputs.get('body')
        state = inputs.get('state')
        assignees = inputs.get('assignees')
        labels = inputs.get('labels')
        milestone = inputs.get('milestone')
        
        issue = await GitHubAPI.update_issue(context, owner, repo, issue_number, title, body, state, assignees, labels, milestone)
        
        # Transform the response to include relevant information
        return {
            'number': issue['number'],
            'title': issue['title'],
            'description': issue['body'],
            'state': issue['state'],
            'created_at': issue['created_at'],
            'updated_at': issue['updated_at'],
            'closed_at': issue['closed_at'],
            'author': {
                'login': issue['user']['login'],
                'avatar_url': issue['user']['avatar_url']
            },
            'assignees': [{'login': assignee['login']} for assignee in issue.get('assignees', [])],
            'labels': [{'name': label['name'], 'color': label['color']} for label in issue.get('labels', [])],
            'url': issue['html_url']
        }

@github.action("get_issue_comments")
class GetIssueComments(ActionHandler):
    """
    Action that retrieves comments for an issue.
    """
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        owner = inputs['owner']
        repo = inputs['repo']
        issue_number = inputs['issue_number']
        
        comments = await GitHubAPI.get_issue_comments(context, owner, repo, issue_number)
        
        # Transform the response to include relevant information
        return [{
            'id': comment['id'],
            'body': comment['body'],
            'created_at': comment['created_at'],
            'updated_at': comment['updated_at'],
            'author': {
                'login': comment['user']['login'],
                'avatar_url': comment['user']['avatar_url']
            },
            'url': comment['html_url']
        } for comment in comments]

@github.action("get_pull_request")
class GetPullRequest(ActionHandler):
    """
    Action that retrieves detailed information about a specific pull request.
    """
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        owner = inputs['owner']
        repo = inputs['repo']
        pull_number = inputs['pull_number']
        
        pr = await GitHubAPI.get_pull_request(context, owner, repo, pull_number)
        
        # Transform the response to include relevant information
        return {
            'number': pr['number'],
            'title': pr['title'],
            'description': pr['body'],
            'state': pr['state'],
            'created_at': pr['created_at'],
            'updated_at': pr['updated_at'],
            'merged_at': pr['merged_at'],
            'closed_at': pr['closed_at'],
            'draft': pr['draft'],
            'mergeable': pr.get('mergeable'),
            'mergeable_state': pr.get('mergeable_state'),
            'merged': pr['merged'],
            'author': {
                'login': pr['user']['login'],
                'avatar_url': pr['user']['avatar_url']
            },
            'assignees': [{'login': assignee['login']} for assignee in pr.get('assignees', [])],
            'requested_reviewers': [{'login': reviewer['login']} for reviewer in pr.get('requested_reviewers', [])],
            'labels': [{'name': label['name'], 'color': label['color']} for label in pr.get('labels', [])],
            'head': {
                'ref': pr['head']['ref'],
                'sha': pr['head']['sha'],
                'repo': {
                    'name': pr['head']['repo']['name'],
                    'full_name': pr['head']['repo']['full_name']
                }
            },
            'base': {
                'ref': pr['base']['ref'],
                'sha': pr['base']['sha'],
                'repo': {
                    'name': pr['base']['repo']['name'],
                    'full_name': pr['base']['repo']['full_name']
                }
            },
            'url': pr['html_url']
        }

@github.action("merge_pull_request")
class MergePullRequest(ActionHandler):
    """
    Action that merges a pull request.
    """
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        owner = inputs['owner']
        repo = inputs['repo']
        pull_number = inputs['pull_number']
        commit_title = inputs.get('commit_title')
        commit_message = inputs.get('commit_message')
        merge_method = inputs.get('merge_method', 'merge')
        
        result = await GitHubAPI.merge_pull_request(context, owner, repo, pull_number, 
                                                  commit_title, commit_message, merge_method)
        
        # Transform the response to include relevant information
        return {
            'merged': True,
            'message': result.get('message'),
            'sha': result.get('sha'),
            'commit_title': commit_title or result.get('commit_title'),
            'commit_message': commit_message or result.get('commit_message')
        }

@github.action("create_pull_request_review")
class CreatePullRequestReview(ActionHandler):
    """
    Action that creates a review for a pull request.
    """
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        owner = inputs['owner']
        repo = inputs['repo']
        pull_number = inputs['pull_number']
        body = inputs.get('body')
        event = inputs.get('event')
        comments = inputs.get('comments')
        
        review = await GitHubAPI.create_pull_request_review(context, owner, repo, pull_number, 
                                                          body, event, comments)
        
        # Transform the response to include relevant information
        return {
            'id': review['id'],
            'body': review.get('body'),
            'state': review.get('state'),
            'submitted_at': review.get('submitted_at'),
            'author': {
                'login': review['user']['login'],
                'avatar_url': review['user']['avatar_url']
            },
            'url': review.get('html_url')
        }

@github.action("create_repository")
class CreateRepository(ActionHandler):
    """
    Action that creates a new repository.
    """
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        name = inputs['name']
        description = inputs.get('description')
        private = inputs.get('private', False)
        auto_init = inputs.get('auto_init', False)
        gitignore_template = inputs.get('gitignore_template')
        license_template = inputs.get('license_template')
        org = inputs.get('org')
        
        repo = await GitHubAPI.create_repository(context, name, description, private, 
                                               auto_init, gitignore_template, license_template, org)
        
        # Transform the response to include relevant information
        return {
            'id': repo['id'],
            'name': repo['name'],
            'full_name': repo['full_name'],
            'description': repo['description'],
            'private': repo['private'],
            'default_branch': repo['default_branch'],
            'created_at': repo['created_at'],
            'updated_at': repo['updated_at'],
            'pushed_at': repo['pushed_at'],
            'clone_url': repo['clone_url'],
            'ssh_url': repo['ssh_url'],
            'html_url': repo['html_url']
        }

@github.action("list_branches")
class ListBranches(ActionHandler):
    """
    Action that lists branches for a repository.
    """
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        owner = inputs['owner']
        repo = inputs['repo']
        
        branches = await GitHubAPI.list_branches(context, owner, repo)
        
        # Transform the response to include relevant information
        return [{
            'name': branch['name'],
            'protected': branch['protected'],
            'commit': {
                'sha': branch['commit']['sha'],
                'url': branch['commit']['url']
            }
        } for branch in branches]

@github.action("get_branch_protection")
class GetBranchProtection(ActionHandler):
    """
    Action that retrieves branch protection rules.
    """
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        owner = inputs['owner']
        repo = inputs['repo']
        branch = inputs['branch']
        
        try:
            protection = await GitHubAPI.get_branch_protection(context, owner, repo, branch)
            
            # Transform the response to include relevant information
            return {
                'enabled': True,
                'required_status_checks': protection.get('required_status_checks', {}).get('contexts', []) if protection.get('required_status_checks') else [],
                'enforce_admins': protection.get('enforce_admins', {}).get('enabled', False) if protection.get('enforce_admins') else False,
                'required_pull_request_reviews': {
                    'required_approving_review_count': protection.get('required_pull_request_reviews', {}).get('required_approving_review_count', 0) if protection.get('required_pull_request_reviews') else 0,
                    'dismiss_stale_reviews': protection.get('required_pull_request_reviews', {}).get('dismiss_stale_reviews', False) if protection.get('required_pull_request_reviews') else False,
                    'require_code_owner_reviews': protection.get('required_pull_request_reviews', {}).get('require_code_owner_reviews', False) if protection.get('required_pull_request_reviews') else False
                },
                'restrictions': {
                    'users': [user['login'] for user in protection.get('restrictions', {}).get('users', [])] if protection.get('restrictions') else [],
                    'teams': [team['slug'] for team in protection.get('restrictions', {}).get('teams', [])] if protection.get('restrictions') else []
                }
            }
        except Exception as e:
            if e.status == 404:
                # Branch protection not enabled
                return {
                    'enabled': False
                }
            raise 

@github.action("get_user")
class GetUser(ActionHandler):
    """
    Action that retrieves information about a user.
    """
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        username = inputs['username']
        
        user = await GitHubAPI.get_user(context, username)
        
        # Transform the response to include relevant information
        return {
            'login': user['login'],
            'id': user['id'],
            'name': user.get('name'),
            'company': user.get('company'),
            'blog': user.get('blog'),
            'location': user.get('location'),
            'email': user.get('email'),
            'bio': user.get('bio'),
            'public_repos': user['public_repos'],
            'public_gists': user['public_gists'],
            'followers': user['followers'],
            'following': user['following'],
            'created_at': user['created_at'],
            'updated_at': user['updated_at'],
            'avatar_url': user['avatar_url'],
            'html_url': user['html_url']
        }

@github.action("list_user_repositories")
class ListUserRepositories(ActionHandler):
    """
    Action that lists repositories for a user.
    """
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        username = inputs['username']
        type = inputs.get('type', 'owner')
        sort = inputs.get('sort', 'updated')
        direction = inputs.get('direction', 'desc')
        
        repos = await GitHubAPI.list_user_repositories(context, username, type, sort, direction)
        
        # Transform the response to include relevant information
        return [{
            'id': repo['id'],
            'name': repo['name'],
            'full_name': repo['full_name'],
            'description': repo['description'],
            'private': repo['private'],
            'fork': repo['fork'],
            'created_at': repo['created_at'],
            'updated_at': repo['updated_at'],
            'pushed_at': repo['pushed_at'],
            'language': repo.get('language'),
            'default_branch': repo['default_branch'],
            'visibility': repo.get('visibility'),
            'url': repo['html_url']
        } for repo in repos]

@github.action("list_organization_repositories")
class ListOrganizationRepositories(ActionHandler):
    """
    Action that lists repositories for an organization.
    """
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        org = inputs['org']
        type = inputs.get('type', 'all')
        
        repos = await GitHubAPI.list_organization_repositories(context, org, type)
        
        # Transform the response to include relevant information
        return [{
            'id': repo['id'],
            'name': repo['name'],
            'full_name': repo['full_name'],
            'description': repo['description'],
            'private': repo['private'],
            'fork': repo['fork'],
            'created_at': repo['created_at'],
            'updated_at': repo['updated_at'],
            'pushed_at': repo['pushed_at'],
            'language': repo.get('language'),
            'default_branch': repo['default_branch'],
            'visibility': repo.get('visibility'),
            'url': repo['html_url']
        } for repo in repos]

@github.action("list_organization_members")
class ListOrganizationMembers(ActionHandler):
    """
    Action that lists members of an organization.
    """
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        org = inputs['org']
        role = inputs.get('role', 'all')
        
        members = await GitHubAPI.list_organization_members(context, org, role)
        
        # Transform the response to include relevant information
        return [{
            'login': member['login'],
            'id': member['id'],
            'type': member['type'],
            'site_admin': member['site_admin'],
            'avatar_url': member['avatar_url'],
            'url': member['html_url']
        } for member in members]

@github.action("list_workflows")
class ListWorkflows(ActionHandler):
    """
    Action that lists GitHub Actions workflows for a repository.
    """
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        owner = inputs['owner']
        repo = inputs['repo']
        
        workflows = await GitHubAPI.list_workflows(context, owner, repo)
        
        # Transform the response to include relevant information
        return [{
            'id': workflow['id'],
            'name': workflow['name'],
            'path': workflow['path'],
            'state': workflow['state'],
            'created_at': workflow['created_at'],
            'updated_at': workflow['updated_at'],
            'url': workflow['html_url']
        } for workflow in workflows]

@github.action("get_workflow_runs")
class GetWorkflowRuns(ActionHandler):
    """
    Action that gets runs for a workflow.
    """
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        owner = inputs['owner']
        repo = inputs['repo']
        workflow_id = inputs['workflow_id']
        status = inputs.get('status')
        branch = inputs.get('branch')
        
        runs = await GitHubAPI.get_workflow_runs(context, owner, repo, workflow_id, status, branch)
        
        # Transform the response to include relevant information
        return [{
            'id': run['id'],
            'name': run['name'],
            'workflow_id': run['workflow_id'],
            'head_branch': run['head_branch'],
            'head_sha': run['head_sha'],
            'run_number': run['run_number'],
            'event': run['event'],
            'status': run['status'],
            'conclusion': run['conclusion'],
            'created_at': run['created_at'],
            'updated_at': run['updated_at'],
            'run_started_at': run.get('run_started_at'),
            'run_attempt': run.get('run_attempt', 1),
            'actor': {
                'login': run['actor']['login'],
                'avatar_url': run['actor']['avatar_url']
            },
            'url': run['html_url']
        } for run in runs]

@github.action("create_branch")
class CreateBranch(ActionHandler):
    """
    Action that creates a new branch in a repository.
    """
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        owner = inputs['owner']
        repo = inputs['repo']
        branch_name = inputs['branch_name']
        sha = inputs['sha']  # The SHA of the commit to branch from
        
        result = await GitHubAPI.create_branch(context, owner, repo, branch_name, sha)
        
        # Transform the response to include relevant information
        return {
            'ref': result['ref'],
            'url': result['url'],
            'object': {
                'sha': result['object']['sha'],
                'type': result['object']['type'],
                'url': result['object']['url']
            }
        }

@github.action("create_pull_request")
class CreatePullRequest(ActionHandler):
    """
    Action that creates a new pull request.
    """
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        owner = inputs['owner']
        repo = inputs['repo']
        title = inputs['title']
        head = inputs['head']  # The name of the branch where your changes are implemented
        base = inputs['base']  # The name of the branch you want your changes pulled into
        body = inputs.get('body')
        draft = inputs.get('draft', False)
        maintainer_can_modify = inputs.get('maintainer_can_modify', True)
        
        pr = await GitHubAPI.create_pull_request(context, owner, repo, title, head, base, 
                                               body, draft, maintainer_can_modify)
        
        # Transform the response to include relevant information
        return {
            'number': pr['number'],
            'title': pr['title'],
            'body': pr['body'],
            'state': pr['state'],
            'created_at': pr['created_at'],
            'updated_at': pr['updated_at'],
            'draft': pr['draft'],
            'mergeable': pr.get('mergeable'),
            'mergeable_state': pr.get('mergeable_state'),
            'user': {
                "avatar_url": pr['user']['avatar_url'],
                "login": pr['user']['login'],
                "id": pr['user']['id'],
                "node_id": pr['user']['node_id']
            },
            'assignees': [{'login': assignee['login']} for assignee in pr.get('assignees', [])],
            'requested_reviewers': [{'login': reviewer['login']} for reviewer in pr.get('requested_reviewers', [])],
            'labels': [{'name': label['name'], 'color': label['color']} for label in pr.get('labels', [])],
            'head': {
                'ref': pr['head']['ref'],
                'sha': pr['head']['sha'],
                'repo': {
                    'name': pr['head']['repo']['name'],
                    'full_name': pr['head']['repo']['full_name'],
                    'id': pr['head']['repo']['id']
                }
            },
            'base': {
                'ref': pr['base']['ref'],
                'sha': pr['base']['sha'],
                'repo': {
                    'name': pr['base']['repo']['name'],
                    'full_name': pr['base']['repo']['full_name'],
                    'id': pr['base']['repo']['id']
                }
            },
            'url': pr['html_url'],
        }

@github.action("diff_branch_to_branch")
class DiffBranchToBranch(ActionHandler):
    """
    Action that diffs a branch to another branch.
    """
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        owner = inputs['owner']
        repo = inputs['repo']
        base_branch = inputs['base_branch']
        head_branch = inputs['head_branch']

        diff_data = await GitHubAPI.compare_branches(context, owner, repo, base_branch, head_branch)
        
        # Transform the response to include relevant information
        return {
            'status': diff_data.get('status'),
            'ahead_by': diff_data.get('ahead_by'),
            'behind_by': diff_data.get('behind_by'),
            'total_commits': diff_data.get('total_commits'),
            'commits': [{
                'sha': commit['sha'],
                'author': {
                    'name': commit['commit']['author']['name'],
                    'email': commit['commit']['author']['email'],
                    'date': commit['commit']['author']['date']
                },
                'message': commit['commit']['message'],
                'url': commit['html_url']
            } for commit in diff_data.get('commits', [])],
            'files': [{
                'filename': file['filename'],
                'status': file['status'],
                'additions': file['additions'],
                'deletions': file['deletions'],
                'changes': file['changes'],
                # GitHub sets patch=None for large/binary files; validator needs a string
                'patch': file.get('patch') or ""
            } for file in diff_data.get('files', [])]
        } 
