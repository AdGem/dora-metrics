from github import Github
import datetime
import csv
import os
import datetime
from collections import defaultdict
# Initialize GitHub configuration
g = Github(os.environ.get('GITHUB_PERSONAL_TOKEN'))

# Define the organization and output file
org_name = ""
csv_file_name = "github_deployment_frequency.csv"


def calculate_deployment_frequency(releases, interval):
    # Dictionary to hold counts for each interval
    deployment_counts = defaultdict(int)

    # Filter releases with a valid 'published_at' date
    valid_releases = [release for release in releases if release.published_at]

    # Check if there are valid releases
    if not valid_releases:
        return 0  # Return 0 if no valid releases are found

    # Current date for reference
    current_date = datetime.datetime.utcnow().date()

    for release in valid_releases:
        release_date = release.published_at.date()

        if interval == 'weekly':
            # Get the Monday of the week of the release
            start_of_week = release_date - datetime.timedelta(days=release_date.weekday())
            deployment_counts[start_of_week] += 1

        elif interval == 'monthly':
            # Use year and month as the key
            month_key = (release_date.year, release_date.month)
            deployment_counts[month_key] += 1

        elif interval == 'quarterly':
            # Calculate quarter
            quarter = (release_date.month - 1) // 3 + 1
            quarter_key = (release_date.year, quarter)
            deployment_counts[quarter_key] += 1

    # Calculate average frequency
    oldest_release_date = min(release.published_at for release in valid_releases).date()
    if interval == 'weekly':
        num_intervals = (current_date - oldest_release_date).days // 7
    elif interval == 'monthly':
        num_intervals = (current_date.year - oldest_release_date.year) * 12 + current_date.month - oldest_release_date.month
    elif interval == 'quarterly':
        num_intervals = ((current_date.year - oldest_release_date.year) * 12 + current_date.month - oldest_release_date.month) // 3

    return sum(deployment_counts.values()) / num_intervals if num_intervals else 0


# Open CSV file for writing
with open(csv_file_name, mode='w', newline='', encoding='utf-8') as file:
    csv_writer = csv.writer(file)
    csv_writer.writerow(["Repository", "Weekly Frequency", "Monthly Frequency", "Quarterly Frequency"])

    # Fetch repositories
    organization = g.get_organization(org_name)
    for repo in organization.get_repos():
        print(f"Analyzing repository: {repo.name}")

        # Fetch releases
        releases = repo.get_releases()
        # Calculate frequencies and round them
        weekly_freq = round(calculate_deployment_frequency(releases, "weekly"), 2)
        monthly_freq = round(calculate_deployment_frequency(releases, "monthly"), 2)
        quarterly_freq = round(calculate_deployment_frequency(releases, "quarterly"), 2)

        # Write to CSV
        csv_writer.writerow([repo.name, weekly_freq, monthly_freq, quarterly_freq])
