---
name: skill-xhs-mcp-oper
description: XiaoHongShu (RED/XHS) automation assistant via local MCP service
---

# XHS MCP Skill

XiaoHongShu automation skill via MCP protocol.

## Features

- 13 complete tools
- Login management
- Content search and browsing
- Social interactions (like, favorite, comment)
- Content publishing (images and videos)

## Requirements

- Node.js >= 18
- xhs-mcp-service running on localhost:18060

## Installation

```bash
git clone https://github.com/weznai/xhs-mcp-service.git
cd xhs-mcp-service
npm install
npm run login
npm start
```

## Tools

1. check_login_status - Check login status
2. get_login_qrcode - Get login QR code
3. delete_cookies - Delete login state
4. list_feeds - Get home feed
5. search_feeds - Search notes
6. get_feed_detail - Get note details
7. like_feed - Like/unlike note
8. favorite_feed - Favorite/unfavorite note
9. post_comment_to_feed - Post comment
10. reply_comment_in_feed - Reply to comment
11. user_profile - Get user profile
12. publish_content - Publish image note
13. publish_with_video - Publish video note

## Usage

```javascript
import { searchFeeds, likeFeed } from './src/xhs-tools.js';

const results = await searchFeeds('coffee');
await likeFeed(results.feeds[0].id, results.feeds[0].xsec_token);
```

## License

MIT
