# GitHub Issues Import Scripts

Scripts pour importer automatiquement les tâches en tant que GitHub Issues.

## Installation

```bash
# Installer les dépendances
pip install PyGithub python-dotenv
```

## Configuration

### Option 1 : Variable d'environnement (recommandé)

```bash
# Créer un token personnalisé GitHub
# https://github.com/settings/tokens -> Generate new token (classic)
# Permissions minimales : repo (full control)

# Ajouter à votre shell config (.zshrc, .bashrc)
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxx"

# Ou créer un fichier .env à la racine
echo "GITHUB_TOKEN=ghp_xxxxxxxxxxxxx" > .env
```

### Option 2 : Argument CLI

```bash
python scripts/create_github_issues.py --token ghp_xxxxxxxxxxxxx
```

## Utilisation

### Preview (Dry-run)

Voir les issues qui seraient créées **sans les créer réellement** :

```bash
python scripts/create_github_issues.py --dry-run
```

Output:

```
============================================================
GitHub Issues Import Tool
============================================================
Repository: regi-gouale/mon-service
File: specs/001-church-team-management/github-issues.md
Mode: DRY-RUN (preview only)
============================================================

Parsing issues from markdown...
✓ Found 135 issues

[DRY-RUN] Would create labels:
  - priority:critical
  - priority:important
  - priority:nice-to-have
  - epic:infrastructure
  - epic:authentication
  ...

[1/135] Processing: T0.1.1 - Initialiser le repository...
[DRY-RUN] Would create issue:
  Title: T0.1.1 - Initialiser le repository...
  Epic: Infrastructure
  Priority: 🔴 Critical
  Labels: priority:critical, epic:infrastructure, type:task, 001-church-team-management
  Body preview: Initialiser la structure du monorepo...
```

### Créer les issues réelles

Une fois satisfait du preview, créer les issues :

```bash
# Créer toutes les issues
python scripts/create_github_issues.py

# Créer les 10 premières (pour tester)
python scripts/create_github_issues.py --limit 10

# Personnaliser le repo
python scripts/create_github_issues.py --owner regi-gouale --repo mon-service
```

### Options du script

```bash
python scripts/create_github_issues.py --help

usage: create_github_issues.py [-h] [--token TOKEN] [--owner OWNER]
                               [--repo REPO] [--file FILE] [--dry-run]
                               [--limit LIMIT]

Import GitHub issues from tasks markdown

optional arguments:
  -h, --help            show this help message and exit
  --token TOKEN         GitHub token (or set GITHUB_TOKEN env var)
  --owner OWNER         GitHub owner (default: regi-gouale)
  --repo REPO           GitHub repo (default: mon-service)
  --file FILE           Path to github-issues.md file
  --dry-run             Preview without creating
  --limit LIMIT         Limit number of issues to create
```

## Résultat

Après exécution :

✅ **135 issues créées** dans le repository
✅ **Labels créés automatiquement**:

- `priority:critical` (🔴 red)
- `priority:important` (🟡 orange)
- `priority:nice-to-have` (🟢 green)
- `epic:infrastructure`, `epic:authentication`, etc.
- `type:task`
- `001-church-team-management`
- `effort:1h`, `effort:2h`, etc.

✅ **Issues liées au projet** et prêtes à développer

## Gestion après import

### Dans GitHub

1. Créer un **Project** "Church Team Management"
2. Ajouter les issues au projet
3. Configurer les colonnes (Todo, In Progress, Done)
4. Assigner aux développeurs
5. Grouper par Epic

### Workflow recommandé

```bash
# Créer une branche pour une issue
git checkout -b feat/T0.1.1-init-repo

# Développer
# ...

# Commit avec référence issue
git commit -m "feat: initialiser repository structure

- Créer structure backend/ et frontend/
- Configurer gitignore
- Ajouter README

Fixes #123"

# Push et créer PR
# -> PR auto-liée à issue 123
# -> Ferme l'issue quand merged
```

## Troubleshooting

### ❌ "Error: GitHub token required"

```bash
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxx"
python scripts/create_github_issues.py
```

### ❌ "Error connecting to GitHub"

Vérifier :

- Token valide
- Permissions suffisantes (repo scope)
- Connexion internet

### ❌ "File not found: specs/..."

Lancer le script depuis la racine du repo:

```bash
cd /Users/regigouale/GitHub/mon-service
python scripts/create_github_issues.py
```

### ❌ "Error creating issue: API rate limit exceeded"

GitHub limite à 60 requêtes/heure. Attendre 1 heure ou :

```bash
# Créer les issues par batch
python scripts/create_github_issues.py --limit 20
sleep 3600  # Attendre 1h
python scripts/create_github_issues.py --limit 40
```

## Advanced

### Modifier les issues après creation

Utiliser `gh` CLI ou l'interface GitHub :

```bash
# Éditer une issue via CLI
gh issue edit 123 --label "priority:critical"

# Créer un project et ajouter issues
gh project create --owner regi-gouale --title "Church Team Management"
gh project item-add <project-id> <issue-number>
```

### Exporter les issues

```bash
# Lister les issues du branch
gh issue list --state open --label 001-church-team-management --json title,number,labels

# Export CSV
gh issue list --state open --label 001-church-team-management \
  --json title,number,labels \
  | jq -r '.[] | [.number, .title] | @csv' > issues.csv
```

## Notes

- Script idempotent : créer les mêmes issues 2x ne crée que les nouvelles
- Les labels sont créés automatiquement
- Les assignations doivent être faites manuellement ou ajoutées au script
- Le fichier source `github-issues.md` doit être bien formaté (voir le template)
