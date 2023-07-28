import csv
import re
from github import Github

def clean_issue_title(title):
    if title is None:
        return ""
    # Remove common file extensions like "readme.md" from the title
    title = re.sub(r'\b(readme\.md|readme|LICENSE|CONTRIBUTING)\b', '', title, flags=re.IGNORECASE).strip()
    # Add more patterns to remove if needed
    # title = re.sub(r'pattern_to_remove', '', title).strip()
    return title

def fetch_repo_issues(repo):
    # Fetch all issues for the repository
    issues = repo.get_issues(state="all")

    # Filter out pull requests
    return [issue for issue in issues if not issue.pull_request]

def fetch_all_issues(organization_name, access_token):
    try:
        g = Github(access_token)
        org = g.get_organization(organization_name)

        all_issues = []

        # Fetch all repositories for the organization
        repos = org.get_repos()

        for repo in repos:
            # Fetch issues (excluding pull requests) for each repository and add them to the list
            issues = fetch_repo_issues(repo)
            all_issues.extend(issues)

        return all_issues
    except Exception as e:
        print(f"An error occurred while fetching issues: {e}")
        return []

if __name__ == "__main__":
    organization_name = "Organization-Name" #replace it with ur organization name
    access_token = "Access-Token"           #replace it with your personal access token

    issues = fetch_all_issues(organization_name, access_token)

    with open("issues_with_info.csv", "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["Issue Title", "Issue Number", "Issue URL", "Milestone Title", "Milestone Number", "Milestone Description", "Milestone Due Date", 
                      "Assignees", "Labels", "Closed At", "Closed By", "Created At", "ID", "Locked", "State", "State Reason", "Updated At"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for issue in issues:
            assignees = ", ".join([assignee.login for assignee in issue.assignees]) if issue.assignees else ""
            labels = ", ".join([label.name for label in issue.labels]) if issue.labels else ""

            closed_at_date = issue.closed_at.strftime("%Y-%m-%d") if issue.closed_at else ""
            created_at_date = issue.created_at.strftime("%Y-%m-%d") if issue.created_at else ""
            updated_at_date = issue.updated_at.strftime("%Y-%m-%d") if issue.updated_at else ""

            # Clean up the issue title by removing unwanted patterns
            issue_title = clean_issue_title(issue.title)

            row = {
                "Issue Title": issue_title,
                "Issue Number": issue.number,
                "Issue URL": issue.html_url,
                "Milestone Title": issue.milestone.title if issue.milestone else "",
                "Milestone Number": issue.milestone.number if issue.milestone else "",
                "Milestone Description": issue.milestone.description if issue.milestone else "",
                "Milestone Due Date": issue.milestone.due_on.strftime("%Y-%m-%d") if issue.milestone and issue.milestone.due_on else "",
                "Assignees": assignees,
                "Labels": labels,
                "Closed At": closed_at_date,
                "Closed By": issue.closed_by.login if issue.closed_by else "",
                "Created At": created_at_date,
                "ID": issue.id if issue.id else "",
                "Locked": issue.locked if issue.locked else "",
                "State": issue.state if issue.state else "",
                "State Reason": issue.state_reason if issue.state_reason else "",
                "Updated At": updated_at_date,
            }
            writer.writerow(row)

    print("CSV file 'issues_with_info.csv' has been created successfully.")
