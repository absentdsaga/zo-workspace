---
name: github-repos
description: Create GitHub repositories via API. Use this to create new repositories on your GitHub account.
compatibility: Created for Zo Computer
metadata:
  author: dioni.zo.computer
---

This skill lets you create GitHub repositories from the command line.

## Setup

First, get a GitHub Personal Access Token:
1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Give it a name and select the "repo" scope (allows creating repos)
4. Copy the token

Add the token as a secret in Zo:
- Go to [Settings > Developers](/?t=settings&s=developers)
- Add a secret named `GITHUB_TOKEN` with your token value

## Usage

Run the script from the skill's scripts directory:

```bash
cd /home/workspace/Skills/github-repos/scripts
bun github-repos.ts create --name "my-repo" --description "My new repo" --public
```

### Commands

**create** - Create a new repository

Options:
- `--name <name>` (required): Repository name
- `--description <desc>`: Repository description
- `--public`: Make the repository public (default: private)
- `--auto-init`: Initialize with a README
- `--gitignore <lang>`: Add a .gitignore template (e.g., Python, Node)
- `--license <license>`: Add a LICENSE file (e.g., MIT, Apache-2.0)

Examples:

Create a private repo:
```bash
bun github-repos.ts create --name "my-project"
```

Create a public repo with README:
```bash
bun github-repos.ts create --name "my-project" --public --auto-init
```

Create a Python project:
```bash
bun github-repos.ts create --name "my-python-project" --description "Python utility scripts" --public --auto-init --gitignore Python --license MIT
```

## Notes

- The GitHub token is read from the `GITHUB_TOKEN` environment variable
- Repository names must be unique across your GitHub account
- All repositories are created under the authenticated user's account
