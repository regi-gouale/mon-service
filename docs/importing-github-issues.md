# How to Use the GitHub Issues Importer

## Quick Start

### 1. Get a GitHub Token

Go to https://github.com/settings/tokens and create a new **Personal Access Token (Classic)**

**Minimum permissions required**:

- ✅ `repo` (Full control of private repositories)

Keep this token secure! Never commit it.

### 2. Set up the token

**Option A: Environment variable** (recommended)

```bash
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxx"
```

Or add to your shell config (`~/.zshrc`, `~/.bashrc`):

```bash
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxx"
```

**Option B: .env file**

Create `.env` in the root directory:

```
GITHUB_TOKEN=ghp_xxxxxxxxxxxxx
```

**Option C: Direct argument**

```bash
python scripts/create_github_issues.py --token ghp_xxxxxxxxxxxxx --dry-run
```

### 3. Preview the issues (dry-run)

```bash
python scripts/create_github_issues.py --dry-run
```

Output shows:

- Which labels would be created
- Which issues would be imported
- How many are being processed

✅ **No actual changes** - safe to preview!

### 4. Create the issues

```bash
python scripts/create_github_issues.py
```

This will:

1. Create all labels (priority, epic, effort, etc.)
2. Create all GitHub issues
3. Print a summary

## Command Examples

### Preview only (safe)

```bash
python scripts/create_github_issues.py --dry-run
```

### Create first 10 issues (for testing)

```bash
python scripts/create_github_issues.py --limit 10
```

### Create issues with custom repo

```bash
python scripts/create_github_issues.py --owner your-username --repo your-repo
```

### Full help

```bash
python scripts/create_github_issues.py --help
```

## What Gets Created

### Labels

| Label                          | Color     | Purpose              |
| ------------------------------ | --------- | -------------------- |
| `priority:critical`            | 🔴 Red    | Blocking/Must-do     |
| `priority:important`           | 🟡 Orange | Should-do            |
| `priority:nice-to-have`        | 🟢 Green  | Nice-to-do           |
| `epic:infrastructure`          | Blue      | Epic grouping        |
| `epic:authentication`          | Blue      | Epic grouping        |
| ...                            | ...       | (14 epics total)     |
| `type:task`                    | Gray      | All issues are tasks |
| `effort:1h`, `effort:2h`, etc. | -         | Effort estimation    |

### Issues

135 issues across 12 epics:

```
Epic 0: Infrastructure (24h)
  ├─ T0.1: Repository setup (4h)
  ├─ T0.2: Backend FastAPI (6h)
  ├─ T0.3: Frontend Next.js (6h)
  ├─ T0.4: Database (4h)
  └─ T0.5: CI/CD (4h)

Epic 1: Authentication (36h)
  ├─ T1.1: Backend Auth (8h)
  ├─ T1.2: OAuth (4h)
  ├─ T1.3: Email Service (4h)
  ├─ T1.4: Frontend Auth UI (10h)
  ├─ T1.5: User Profile (4h)
  └─ T1.6: Tests (6h)

[... and 10 more epics ...]
```

## Next Steps in GitHub

After creating issues:

### 1. Create a Project

```bash
# Using gh CLI
gh project create --owner regi-gouale --title "Church Team Management"

# Or manually in GitHub UI:
# https://github.com/regi-gouale/mon-service/projects
```

### 2. Link Issues to Project

```bash
# View project ID
gh project list

# Add issues to project
for issue_num in {1..135}; do
  gh project item-add <PROJECT_ID> <issue_num>
done

# Or manually in GitHub UI
```

### 3. Organize in Columns

Set up columns in project:

- **Backlog** - Not started
- **Ready** - Ready to start
- **In Progress** - Currently working
- **Review** - PR submitted
- **Done** - Completed

### 4. Filter by Epic

Add to project views:

```
is:open label:epic:infrastructure
is:open label:epic:authentication
```

### 5. Start Developing

Pick an issue and start working:

```bash
# Create branch from issue
git checkout -b feat/T0-1-1-init-repo

# Develop...
git commit -m "feat: setup repository structure

Fixes #123"

# Push and create PR
git push origin feat/T0-1-1-init-repo
# Create PR on GitHub -> auto-closes issue when merged
```

## Troubleshooting

### "API rate limit exceeded"

GitHub limits API calls. Wait or create in batches:

```bash
python scripts/create_github_issues.py --limit 20
# Wait 1 hour
python scripts/create_github_issues.py --limit 40
```

### "Error creating issue: Validation Failed"

Issue might already exist or title is duplicated. Check existing issues:

```bash
gh issue list --label 001-church-team-management
```

### "Error: GitHub token required"

Token not found. Make sure it's set:

```bash
# Check if set
echo $GITHUB_TOKEN

# If empty, export it
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxx"
```

### Script not finding issues

Make sure you're in the right directory:

```bash
cd /Users/regigouale/GitHub/mon-service
python scripts/create_github_issues.py --dry-run
```

## Advanced Usage

### Using with GitHub CLI

```bash
# List created issues
gh issue list --label 001-church-team-management

# Search by effort
gh issue list --label epic:infrastructure --label effort:4h

# Assign to yourself
gh issue edit 123 --assignee @me

# Add to multiple labels
gh issue edit 123 --add-label priority:critical

# Close an issue
gh issue close 123
```

### Bulk operations

```bash
# Mark all effort:1h as ready
gh issue list --label effort:1h --label 001-church-team-management \
  --json number \
  | jq -r '.[] | .number' \
  | xargs -I {} gh issue edit {} --add-label status:ready

# Create a milestone
gh release create "v0.1.0-mvp" --generate-notes

# Link issues to milestone
gh issue list --label epic:infrastructure \
  --json number \
  | jq -r '.[] | .number' \
  | xargs -I {} gh issue edit {} --milestone "MVP"
```

## FAQ

**Q: Can I run this multiple times?**  
A: Yes, it's safe. Duplicate issues won't be created, only new ones.

**Q: Can I modify issues after creation?**  
A: Yes, edit them in GitHub or via CLI:

```bash
gh issue edit 123 --title "New title"
gh issue edit 123 --label priority:critical
```

**Q: Can I delete issues if something goes wrong?**  
A: Yes, delete via GitHub UI or close them. Script won't re-create closed issues.

**Q: How do I update the issue descriptions?**  
A: Edit `github-issues.md` and use the script again. New issues will be created for modified ones.

**Q: Can I export the issues for backup?**  
A: Yes:

```bash
gh issue list --label 001-church-team-management \
  --json title,number,body,labels \
  > issues-backup.json
```

## Support

For issues with the script, check:

- [PyGithub Documentation](https://pygithub.readthedocs.io/)
- [GitHub API Documentation](https://docs.github.com/en/rest)
- [GitHub CLI Reference](https://cli.github.com/manual/)
