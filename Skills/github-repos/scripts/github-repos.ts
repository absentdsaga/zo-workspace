#!/usr/bin/env bun

interface CreateRepoOptions {
  name: string;
  description?: string;
  private?: boolean;
  autoInit?: boolean;
  gitignore?: string;
  license?: string;
}

async function createRepo(options: CreateRepoOptions) {
  const token = process.env.github_token;
  
  if (!token) {
    console.error('Error: GITHUB_TOKEN environment variable not set');
    console.error('Add your GitHub token as a secret in Settings > Developers');
    process.exit(1);
  }

  const { name, description, private: isPrivate = true, autoInit, gitignore, license } = options;

  const body: Record<string, any> = {
    name,
    private: isPrivate,
  };

  if (description) body.description = description;
  if (autoInit) body.auto_init = true;
  if (gitignore) body.gitignore_template = gitignore;
  if (license) body.license_template = license;

  try {
    const response = await fetch('https://api.github.com/user/repos', {
      method: 'POST',
      headers: {
        'Authorization': `token ${token}`,
        'Accept': 'application/vnd.github.v3+json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`GitHub API error: ${response.status} - ${error}`);
    }

    const repo = await response.json();
    
    console.log(`✓ Repository created successfully!`);
    console.log(`  Name: ${repo.full_name}`);
    console.log(`  URL: ${repo.html_url}`);
    console.log(`  Private: ${repo.private}`);
    if (repo.description) console.log(`  Description: ${repo.description}`);
    
  } catch (error) {
    console.error('Failed to create repository:', error);
    process.exit(1);
  }
}

function printHelp() {
  console.log(`
GitHub Repository Creator

Usage:
  bun github-repos.ts create --name <name> [options]

Commands:
  create          Create a new repository

Options:
  --name <name>         Repository name (required)
  --description <desc>  Repository description
  --public              Make repository public (default: private)
  --auto-init           Initialize with README
  --gitignore <lang>    Add .gitignore template (e.g., Python, Node)
  --license <license>   Add LICENSE file (e.g., MIT, Apache-2.0)
  --help                Show this help message

Examples:
  bun github-repos.ts create --name "my-project"
  bun github-repos.ts create --name "my-project" --public --auto-init
  bun github-repos.ts create --name "my-python-project" --description "Python utility" --public --auto-init --gitignore Python --license MIT
`);
}

async function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0 || args.includes('--help')) {
    printHelp();
    process.exit(0);
  }

  const command = args[0];
  
  if (command !== 'create') {
    console.error(`Unknown command: ${command}`);
    printHelp();
    process.exit(1);
  }

  const options: CreateRepoOptions = { name: '' };
  
  for (let i = 1; i < args.length; i++) {
    const arg = args[i];
    
    if (arg === '--name' && args[i + 1]) {
      options.name = args[++i];
    } else if (arg === '--description' && args[i + 1]) {
      options.description = args[++i];
    } else if (arg === '--public') {
      options.private = false;
    } else if (arg === '--auto-init') {
      options.autoInit = true;
    } else if (arg === '--gitignore' && args[i + 1]) {
      options.gitignore = args[++i];
    } else if (arg === '--license' && args[i + 1]) {
      options.license = args[++i];
    }
  }

  if (!options.name) {
    console.error('Error: --name is required');
    printHelp();
    process.exit(1);
  }

  await createRepo(options);
}

main();