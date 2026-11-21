# Security and secret handling

## Environment variables

Copy `backend/.env.example` to `backend/.env` for local development and fill in your own credentials. The real `.env` file is intentionally excluded from version control.

Never commit database connection strings, API keys, access tokens, passwords, or production configuration. Use your deployment platform's secret manager for deployed environments.

## Previously committed credentials

Removing a credential file from the current branch does **not** remove it from earlier Git commits, forks, cached clones, or downloaded archives.

If a real credential was ever committed:

1. Rotate or revoke it immediately at the issuing provider. Treat database URLs and model-provider keys as exposed.
2. Update the value in local and deployment secret stores.
3. Review provider access logs and database activity for unexpected use.
4. If the repository is public or shared, coordinate a history rewrite using a tool such as `git filter-repo`, then force-push only after coordinating with every collaborator. A history rewrite does not replace credential rotation.

Do not paste secret values into issues, pull requests, logs, or chat.
