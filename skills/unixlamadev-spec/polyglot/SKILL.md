---
name: polyglot
description: Translate text to any language with cultural notes
acceptLicenseTerms: true
metadata:
  clawdbot:
    emoji: "🌐"
    homepage: https://aiprox.dev
    requires:
      env:
        - AIPROX_SPEND_TOKEN
---

# Polyglot

Translate text between any languages with cultural context and nuance. Detects source language automatically and provides notes on idioms, formality, and cultural considerations.

## When to Use

- Translating documents or messages
- Understanding foreign language content
- Localizing content with cultural awareness
- Learning about linguistic nuances

## Usage Flow

1. Provide text to translate
2. Specify target language
3. Optionally add context or formality preferences
4. AIProx routes to the polyglot agent
5. Returns translation, detected source language, and cultural notes

## Security Manifest

| Permission | Scope | Reason |
|------------|-------|--------|
| Network | aiprox.dev | API calls to orchestration endpoint |
| Env Read | AIPROX_SPEND_TOKEN | Authentication for paid API |

## Make Request

```bash
curl -X POST https://aiprox.dev/api/orchestrate \
  -H "Content-Type: application/json" \
  -H "X-Spend-Token: $AIPROX_SPEND_TOKEN" \
  -d '{
    "text": "The early bird catches the worm",
    "target_language": "Japanese",
    "task": "translate with cultural equivalent"
  }'
```

### Response

```json
{
  "translation": "早起きは三文の徳 (Hayaoki wa sanmon no toku)",
  "source_language": "English",
  "cultural_notes": "Literal translation would lose meaning. Used equivalent Japanese proverb meaning 'waking early brings three mon (coins) of virtue.' Both emphasize benefits of rising early, though Japanese version focuses on small but certain gains."
}
```

## Trust Statement

Polyglot processes text for translation only. Content is not stored or logged beyond the transaction. Translation is performed by Claude via LightningProx. Your spend token is used for payment only.
