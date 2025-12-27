#!/usr/bin/env python3
"""
Script to import GitHub Issues from tasks.md

Usage:
    python scripts/create_github_issues.py --token YOUR_GITHUB_TOKEN --dry-run
    python scripts/create_github_issues.py --token YOUR_GITHUB_TOKEN

Requirements:
    pip install PyGithub python-dotenv
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from github import Github, GithubException

# Load environment variables
load_dotenv()

# Configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = "regi-gouale"
REPO_NAME = "mon-service"
FEATURE_BRANCH = "001-church-team-management"

# Priority colors
PRIORITY_LABELS = {
    "🔴": {"name": "priority:critical", "color": "d62728"},
    "🟡": {"name": "priority:important", "color": "ff7f0e"},
    "🟢": {"name": "priority:nice-to-have", "color": "2ca02c"},
}

# Epic mapping
EPIC_LABEL_MAP = {
    "Infrastructure & Fondations": "epic:infrastructure",
    "Inscription et Authentification": "epic:authentication",
    "Saisie des Indisponibilités": "epic:availability",
    "Génération et Publication du Planning": "epic:planning",
    "Gestion des Membres du Département": "epic:members",
    "Notifications et Rappels": "epic:notifications",
    "Gestion du Code Vestimentaire": "epic:dresscode",
    "Comptes-Rendus de Service": "epic:reports",
    "Gestion de l'Inventaire": "epic:inventory",
    "Calendrier des Dates Importantes": "epic:events",
    "Liste de Courses Partagée": "epic:shopping",
    "Dashboard & Polish": "epic:dashboard",
}


class IssueParser:
    """Parse issues from markdown file"""

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.issues = []
        self.parse()

    def parse(self):
        """Parse markdown file and extract issues"""
        with open(self.filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Split by H3 headings (### Issue ...)
        issue_blocks = re.split(r"^### Issue ", content, flags=re.MULTILINE)[1:]

        for block in issue_blocks:
            issue = self._parse_issue_block(block)
            if issue:
                self.issues.append(issue)

    def _parse_issue_block(self, block: str) -> Optional[dict]:
        """Parse a single issue block"""
        lines = block.split("\n")
        if not lines:
            return None

        # Extract title (first line)
        title = lines[0].strip()

        # Extract metadata
        metadata = {}
        body_start = 0

        for i, line in enumerate(lines[1:], 1):
            if line.startswith("**"):
                # Metadata line
                match = re.match(r"\*\*(.+?)\*\*:\s*(.+)", line)
                if match:
                    key, value = match.groups()
                    metadata[key.lower()] = value.strip()
            else:
                body_start = i
                break

        # Extract body (everything after metadata)
        body = "\n".join(lines[body_start:]).strip()

        return {
            "title": title,
            "epic": metadata.get("epic", "Infrastructure"),
            "priority": metadata.get("priority", "🟡"),
            "effort": metadata.get("effort", "Unknown"),
            "body": body,
        }


class GitHubIssueCreator:
    """Create GitHub issues from parsed data"""

    def __init__(self, token: str, owner: str, repo: str, dry_run: bool = False):
        self.dry_run = dry_run
        self.g = Github(token) if not dry_run else None
        self.repo = None
        self.owner = owner
        self.repo_name = repo

        if not dry_run:
            try:
                self.repo = self.g.get_user(owner).get_repo(repo)
                print(f"✓ Connected to {owner}/{repo}")
            except GithubException as e:
                print(f"✗ Error connecting to GitHub: {e}")
                sys.exit(1)

        self._ensure_labels()

    def _ensure_labels(self):
        """Ensure all required labels exist"""
        if self.dry_run:
            print("[DRY-RUN] Would create labels:")
            for labels in PRIORITY_LABELS.values():
                print(f"  - {labels['name']}")
            for label in EPIC_LABEL_MAP.values():
                print(f"  - {label}")
            return

        existing_labels = {label.name for label in self.repo.get_labels()}

        labels_to_create = {}
        for priority_label in PRIORITY_LABELS.values():
            labels_to_create[priority_label["name"]] = priority_label["color"]

        for epic_label in EPIC_LABEL_MAP.values():
            if epic_label not in labels_to_create:
                labels_to_create[epic_label] = "a2eeef"  # Default blue

        for label_name, color in labels_to_create.items():
            if label_name not in existing_labels:
                try:
                    self.repo.create_label(name=label_name, color=color)
                    print(f"✓ Created label: {label_name}")
                except GithubException as e:
                    print(f"✗ Error creating label {label_name}: {e}")

    def create_issue(self, issue: dict) -> bool:
        """Create a single GitHub issue"""
        title = issue["title"]
        body = issue["body"]
        epic = issue["epic"]
        priority = issue["priority"]

        # Build labels
        labels = []
        if priority in PRIORITY_LABELS:
            labels.append(PRIORITY_LABELS[priority]["name"])

        if epic in EPIC_LABEL_MAP:
            labels.append(EPIC_LABEL_MAP[epic])

        labels.append("type:task")  # All these are tasks
        labels.append(FEATURE_BRANCH)  # Feature branch label

        # Add effort as label
        effort = issue.get("effort", "Unknown")
        if effort != "Unknown":
            effort_label = effort.replace(" ", "-").lower()
            labels.append(f"effort:{effort_label}")

        if self.dry_run:
            print(f"\n[DRY-RUN] Would create issue:")
            print(f"  Title: {title}")
            print(f"  Epic: {epic}")
            print(f"  Priority: {priority}")
            print(f"  Labels: {', '.join(labels)}")
            print(f"  Body preview: {body[:100]}...")
            return True

        try:
            self.repo.create_issue(
                title=title,
                body=body,
                labels=labels,
            )
            print(f"✓ Created: {title}")
            return True
        except GithubException as e:
            print(f"✗ Error creating issue '{title}': {e}")
            return False

    def create_issues(self, issues: list) -> dict:
        """Create multiple issues"""
        stats = {"total": len(issues), "created": 0, "failed": 0}

        for i, issue in enumerate(issues, 1):
            print(f"\n[{i}/{stats['total']}] Processing: {issue['title']}")
            if self.create_issue(issue):
                stats["created"] += 1
            else:
                stats["failed"] += 1

        return stats


def main():
    parser = argparse.ArgumentParser(
        description="Import GitHub issues from tasks markdown"
    )
    parser.add_argument("--token", help="GitHub token (or set GITHUB_TOKEN env var)")
    parser.add_argument(
        "--owner", default=REPO_OWNER, help="GitHub owner (default: regi-gouale)"
    )
    parser.add_argument(
        "--repo", default=REPO_NAME, help="GitHub repo (default: mon-service)"
    )
    parser.add_argument(
        "--file",
        default="specs/001-church-team-management/github-issues.md",
        help="Path to github-issues.md file",
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview without creating")
    parser.add_argument(
        "--limit", type=int, help="Limit number of issues to create"
    )

    args = parser.parse_args()

    # Get token from args or env
    token = args.token or GITHUB_TOKEN
    if not token:
        print("✗ Error: GitHub token required")
        print("  Set GITHUB_TOKEN env var or use --token flag")
        sys.exit(1)

    # Check file exists
    if not Path(args.file).exists():
        print(f"✗ Error: File not found: {args.file}")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"GitHub Issues Import Tool")
    print(f"{'='*60}")
    print(f"Repository: {args.owner}/{args.repo}")
    print(f"File: {args.file}")
    if args.dry_run:
        print(f"Mode: DRY-RUN (preview only)")
    print(f"{'='*60}\n")

    # Parse issues
    print("Parsing issues from markdown...")
    issue_parser = IssueParser(args.file)
    print(f"✓ Found {len(issue_parser.issues)} issues\n")

    # Limit if specified
    issues = issue_parser.issues
    if args.limit:
        issues = issues[: args.limit]
        print(f"Limited to {args.limit} issues\n")

    # Create issues
    creator = GitHubIssueCreator(token, args.owner, args.repo, args.dry_run)
    stats = creator.create_issues(issues)

    # Summary
    print(f"\n{'='*60}")
    print(f"Summary")
    print(f"{'='*60}")
    print(f"Total: {stats['total']}")
    print(f"Created: {stats['created']}")
    print(f"Failed: {stats['failed']}")

    if args.dry_run:
        print(f"\n✓ Dry-run complete. No issues created.")
        print(f"Run without --dry-run to create issues.")
    else:
        print(f"\n✓ Issues created successfully!")

    print(f"{'='*60}\n")

    return 0 if stats["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
