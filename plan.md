

## Forum Notifier Bot — Final Design Document

### Overview

A single-server Discord bot that monitors forum channels and posts embed notifications with buttons when new posts are created. Configured via slash commands with JSON persistence.

---

### Tech Stack

- **Language:** Python 3.10+
- **Library:** discord.py (v2.0+)
- **Data Storage:** JSON file
- **Hosting:** Local PC

---

### Project Structure

```
forum-notifier-bot/
├── bot.py                  # Entry point, bot initialization
├── cogs/
│   ├── forum_listener.py   # Thread create event handler
│   └── config_commands.py  # Slash commands
├── utils/
│   └── storage.py          # JSON read/write helpers
├── data/
│   └── settings.json       # Persisted configuration
├── requirements.txt
└── .env                    # Bot token
```

---

### Configuration Schema

```json
{
  "notification_channel_id": null,
  "error_channel_id": null,
  "monitored_forums": [],
  "embed_color": "#2f3136",
  "preview_length": 100
}
```

| Key                       | Type        | Description                     |
| ------------------------- | ----------- | ------------------------------- |
| `notification_channel_id` | int or null | Where notifications post        |
| `error_channel_id`        | int or null | Where errors get reported       |
| `monitored_forums`        | list[int]   | Forum channel IDs to watch      |
| `embed_color`             | string      | Hex color for embeds            |
| `preview_length`          | int         | Characters to preview from post |

---

### Slash Commands

All commands require **Administrator** permission.

| Command                | Parameters  | Description                    |
| ---------------------- | ----------- | ------------------------------ |
| `/forum monitor`       | `channel`   | Add a forum to the watch list  |
| `/forum unmonitor`     | `channel`   | Remove a forum from monitoring |
| `/forum list`          | —           | Show all monitored forums      |
| `/forum notifications` | `channel`   | Set notification channel       |
| `/forum errors`        | `channel`   | Set error reporting channel    |
| `/forum color`         | `hex_color` | Set embed color                |
| `/forum preview`       | `length`    | Set preview character count    |
| `/forum settings`      | —           | Display all current settings   |
| `/forum test`          | —           | Send a test notification       |

---

### Notification Embed Structure

```
┌──────────────────────────────────────────────────┐
│ 📝 New Post in #help-forum                       │  ← Embed title
├──────────────────────────────────────────────────┤
│                                                  │
│ **How do I improve my aim?**                     │  ← Post title
│                                                  │
│ "I've been playing for a few months now and I   │  ← Preview text
│ feel stuck around Gold rank..."                  │     (100 chars default)
│                                                  │
├──────────────────────────────────────────────────┤
│ 👤 Posted by                                     │  ← Field name
│ @Username                                        │  ← Field value (mention)
├──────────────────────────────────────────────────┤
│ Today at 3:45 PM                                 │  ← Footer + timestamp
└──────────────────────────────────────────────────┘
  [ 🔗 Jump to Post ]  [ 📁 View Forum ]            ← Buttons (link type)
```

**Default embed color:** `#2f3136` (Discord's dark grey)

---

### Event Flow

```
on_thread_create(thread)
    │
    ├─► Is thread.parent_id in monitored_forums?
    │       No  → return (ignore)
    │       Yes → continue
    │
    ├─► Is thread.newly_created?
    │       No  → return (ignore archived/unarchived)
    │       Yes → continue
    │
    ├─► Is notification_channel_id set?
    │       No  → log warning, return
    │       Yes → continue
    │
    ├─► Build embed
    │       • Title: "📝 New Post in #{forum_name}"
    │       • Description: **{thread.name}**\n\n"{preview}..."
    │       • Field: Posted by → thread.owner.mention
    │       • Footer: timestamp
    │       • Color: from config
    │
    ├─► Build buttons (View.Link style)
    │       • "Jump to Post" → thread.jump_url
    │       • "View Forum" → parent forum URL
    │
    └─► Send to notification channel
            • On success → done
            • On error → send to error channel (if configured)
```

---

### Error Handling

| Error                                     | Action                                            |
| ----------------------------------------- | ------------------------------------------------- |
| Notification channel deleted/inaccessible | Post to error channel                             |
| Forum channel deleted                     | Remove from monitored list, post to error channel |
| Missing permissions                       | Post to error channel with details                |
| JSON file corrupted                       | Recreate with defaults, post to error channel     |
| Error channel also broken                 | Log to console only                               |

---

### Bot Permissions Required

```
- View Channels
- Send Messages
- Embed Links
- Use External Emojis (optional, for custom emoji in buttons)
```

**Permission integer:** `84992`

---

### Dependencies

```
# requirements.txt
discord.py>=2.0
python-dotenv
```

---

### Files Summary

| File                      | Responsibility                                 |
| ------------------------- | ---------------------------------------------- |
| `bot.py`                  | Initialize bot, load cogs, run                 |
| `cogs/forum_listener.py`  | `on_thread_create` event, embed builder        |
| `cogs/config_commands.py` | All `/forum` slash commands                    |
| `utils/storage.py`        | `load_settings()`, `save_settings()`, defaults |
| `data/settings.json`      | Persisted config data                          |
| `.env`                    | `DISCORD_TOKEN=xxx`                            |

---

### Future Enhancements (Phase 2+)

- Web dashboard for visual configuration
- Per-forum notification channels
- Custom embed templates per forum
- Role ping options per forum
- Analytics (post count, popular forums)

---


