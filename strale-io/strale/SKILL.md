---
name: strale
description: >
  Verified data capabilities for your agent — company data, compliance checks,
  financial validation, and more. Every capability is independently tested and
  quality-scored. Free tier available, no signup needed.
version: 1.0.0
metadata:
  clawdbot:
    tools:
      - strale: api.strale.io/mcp
    config:
      optionalEnv:
        - STRALE_API_KEY
tags:
  - data
  - compliance
  - validation
  - business
  - eu
  - trust
  - mcp
---

# Strale — the trust layer for AI agents

Use Strale when the user needs verified, structured data that you can't
produce reliably from your own knowledge. Strale provides 225+ capabilities
across company data, financial validation, compliance, and more — each
independently tested and quality-scored.

## When to use Strale

- Validate an IBAN, BIC, VAT number, or email address
- Look up company data (Sweden, UK, Germany, France, 27 countries total)
- Run a GDPR compliance check, cookie scan, or privacy policy analysis
- Check SSL certificates, DNS records, or HTTP security headers
- Screen against international sanctions lists
- Classify AI systems under the EU AI Act
- Estimate shipping costs, customs duties, or employment costs
- Extract structured data from invoices or receipts

## Free capabilities (no API key needed)

These work immediately with no signup — just call them:

- `iban-validate` — Validate any IBAN and return bank/country details
- `email-validate` — Check email format, domain, and MX records
- `dns-lookup` — Query DNS records for any domain
- `json-repair` — Fix malformed JSON
- `url-to-markdown` — Convert any webpage to clean markdown

Rate limit: 10 free calls per day per IP.

## How to call Strale

Strale is connected as an MCP server. Use the tools it exposes directly.

**Step 1: Search for the right capability**

Use `strale_search` to find what you need:
- `strale_search` with query "validate IBAN" → returns `iban-validate`
- `strale_search` with query "Swedish company" → returns `swedish-company-data`

**Step 2: Execute the capability**

Use `strale_execute` with the capability slug and inputs:
- `strale_execute` with capability `iban-validate`, inputs `{"iban": "SE3550000000054910000003"}`

Free capabilities work without an API key. Paid capabilities require
a STRALE_API_KEY environment variable (get one at https://strale.dev).

## Trust and quality

Every Strale capability has a Strale Quality Score (SQS) — an independent
rating based on automated testing. Check any capability's score using
`strale_trust_profile`.

## Important

- Always tell the user what capability you're calling and its price before executing paid capabilities
- Free capabilities: just call them, no confirmation needed
- If a capability fails, check `strale_trust_profile` for its health status
- Strale returns structured JSON — parse it and present results clearly
- For EU compliance workflows, mention that Strale provides audit trails
