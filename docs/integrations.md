# Design & Productivity Integrations

This guide documents the supported SDKs for Figma, Notion, and Slack, with Node.js/TypeScript and Python examples. Ensure `.env` remains uncommitted and includes the required tokens.

## Environment Variables

```bash
FIGMA_TOKEN=...   # Personal access token from Figma
NOTION_TOKEN=...  # Notion integration secret
SLACK_TOKEN=...   # Slack bot token
```

## Node.js / TypeScript

Install the official or community SDKs via npm:

```bash
# Figma REST API client (community SDK)
npm install figma-js                # OR: npm install @figma-js/sdk

# Notion API client (official)
npm install @notionhq/client

# Slack Web API client (official)
npm install @slack/web-api

# If you want to generate types or interact with Figma design tokens
npm install --save-dev figma-export
```

Example usage:

```ts
// figma.ts
import { Client as FigmaClient } from 'figma-js';

export const figma = FigmaClient({ personalAccessToken: process.env.FIGMA_TOKEN });

// notion.ts
import { Client as NotionClient } from '@notionhq/client';

export const notion = new NotionClient({ auth: process.env.NOTION_TOKEN });

// slack.ts
import { WebClient } from '@slack/web-api';

export const slack = new WebClient(process.env.SLACK_TOKEN);
```

For Figma tokens export via CLI:

```bash
# Install globally
npm install -g figma-export

# Or run via npx
npx figma-export tokens --file-id <your-file-id> --token <your-figma-token>
```

## Python

Install the corresponding packages with pip:

```bash
# Figma API (community library)
pip install figma-python

# Notion SDK (official)
pip install notion-client

# Slack SDK (official)
pip install slack-sdk

# If you need Google credentials for Sheets or others:
pip install google-auth-httplib2 google-auth-oauthlib
```

Example usage:

```python
import os
from figma import Figma
from notion_client import Client as NotionClient
from slack_sdk import WebClient

figma_client = Figma(access_token=os.getenv("FIGMA_TOKEN"))
notion_client = NotionClient(auth=os.getenv("NOTION_TOKEN"))
slack_client = WebClient(token=os.getenv("SLACK_TOKEN"))

# Example: fetch a Figma file
# file = figma_client.file("FIGMA_FILE_KEY")
```

Export environment variables for local sessions:

```bash
export FIGMA_TOKEN=<your-figma-token>
export NOTION_TOKEN=<your-notion-integration-secret>
export SLACK_TOKEN=<your-slack-bot-token>
```
