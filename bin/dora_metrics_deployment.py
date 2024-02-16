from github import Github
import os

# Initialize GitHub configuration
g = Github(os.environ.get('GITHUB_PERSONAL_TOKEN'))
org_name = ""  #
# List of specific repositories you want to fetch data from
repo_names = [""] 


for repo in g.get_organization(org_name).get_repos():
    print(repo.name)
# Function to get deployment data from a repository's releases
def get_deployments_from_releases(repo):
    deployments = []
    for release in repo.get_releases():
        if release.published_at is None:
            continue  # Skip drafts or prereleases

        #  extract a commit SHA from tag, if tags are used for releases
        try:
            commit_sha = repo.get_git_ref(f"tags/{release.tag_name}").object.sha
        except:
            commit_sha = None

        deployment = {
            "service": repo.name,
            "start_time": int(release.published_at.timestamp() * 1e9),  # Convert to nanoseconds
            "end_time": int(release.published_at.timestamp() * 1e9),    # Assuming start and end time are the same for a release
            "commit_sha": commit_sha,
            "repo_url": repo.html_url,
            "env": "prod"  # Set your environment as needed
        }
        deployments.append(deployment)
    return deployments

# Fetch deployment data from specified repositories
all_deployments = []
for repo_name in repo_names:
    try:
        repo = g.get_repo(f"{org_name}/{repo_name}")
        print(f"Fetching deployments from repository: {repo.name}")
        deployments = get_deployments_from_releases(repo)
        all_deployments.extend(deployments)
        # Output the deployment data
        print(all_deployments)
    except Exception as e:
        print(f"Error fetching repository {repo_name}: {e}")

