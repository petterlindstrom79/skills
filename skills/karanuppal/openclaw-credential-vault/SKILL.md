---
name: openclaw-credential-vault
description: Encrypted credential management for OpenClaw — keeps API keys, tokens, and passwords out of the AI agent's context window. AES-256-GCM encryption, subprocess-scoped injection, automatic output scrubbing.
metadata: {"openclaw":{"emoji":"🔐","homepage":"https://github.com/karanuppal/openclaw-credential-vault"}}
---

# OpenClaw Credential Vault

Encrypted credential management for OpenClaw. Keeps API keys, tokens, and passwords out of the AI agent's context window — where they could be exfiltrated, leaked into transcripts, or exposed through tool output.

## What You Get

- **Credentials never enter the AI's context.** Decrypted and injected only into the specific subprocess that needs them, then scrubbed from output before the agent sees it.
- **Encryption at rest.** Each credential individually encrypted with AES-256-GCM, Argon2id key derivation.
- **Automatic output scrubbing.** Multiple independent scrubbing layers catch credentials in tool output, outbound messages, and session transcripts.
- **~700 tests** across 36 files covering crypto, injection, scrubbing, adversarial attacks, and end-to-end scenarios.

## Install

Install via the OpenClaw plugin system:

```bash
openclaw plugins install openclaw-credential-vault
```

Then restart the gateway to load the plugin. Full installation options and documentation at the [GitHub repository](https://github.com/karanuppal/openclaw-credential-vault).

## Quick Start

```bash
# Initialize the vault
openclaw vault init

# Add a credential (interactive — picks the right injection type)
openclaw vault add github --key "ghp_your_token_here"

# Verify it works
openclaw vault test github

# Add more
openclaw vault add stripe --key "sk_live_..."
openclaw vault add npm --key "npm_..."
```

That's it. Your agent can now use `gh`, call Stripe APIs, and publish npm packages without ever seeing the credentials.

## How It Works

When the agent runs a tool like `gh pr list`:

1. The vault matches the command to a stored credential
2. Decrypts the credential and injects it into the subprocess environment
3. The tool runs with the credential, returns results
4. The subprocess exits — the credential dies with it
5. Output is scrubbed for credential patterns before the agent sees it
6. The agent gets clean results — no credential anywhere in context

This also works for API calls with header injection (Authorization headers added automatically for matching URL patterns).

## Commands

- `vault init` — Initialize vault
- `vault add <tool> --key <cred>` — Add a credential (interactive usage selection: API, CLI)
- `vault list` — Show all stored credentials and status
- `vault show <tool>` — Show credential details and injection config
- `vault test <tool>` — Verify injection and scrubbing work end-to-end
- `vault rotate <tool> --key <new>` — Rotate a credential
- `vault rotate --check` — Show credentials overdue for rotation
- `vault remove <tool>` — Remove a credential

### Non-Interactive Mode

```bash
# API header injection
openclaw vault add stripe --key "sk_live_..." --use api --url "api.stripe.com/*" --yes

# CLI env injection
openclaw vault add github --key "ghp_..." --use cli --command gh --env GITHUB_TOKEN --yes
```

## Security Model

1. **Agent never sees credentials** — injection happens at the subprocess/hook level
2. **Encryption at rest** — AES-256-GCM with per-credential salts
3. **Key derivation** — Argon2id (memory-hard, resistant to GPU cracking)
4. **Subprocess isolation** — credentials exist only in the child process environment, die when it exits
5. **Output scrubbing** — multiple independent hooks catch credential leaks before they reach the agent's context
6. **Open source** — full source code and test suite available for review

## Links

- GitHub: https://github.com/karanuppal/openclaw-credential-vault
- npm: https://www.npmjs.com/package/openclaw-credential-vault
- Issues: https://github.com/karanuppal/openclaw-credential-vault/issues
