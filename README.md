# Forum Notifier Bot

A Discord bot that monitors forum channels and automatically posts notifications when new threads are created. Includes customizable embeds, link buttons, and administrator slash commands for configuration.

## Features

- **Automatic Notifications**: Detects new posts in monitored forum channels
- **Rich Embeds**: Displays post title, preview text, author, and timestamp
- **Quick Navigation**: "Jump to Post" and "View Forum" buttons on each notification
- **Slash Commands**: Easy configuration through Discord's native command system
- **Flexible Settings**: Customize embed colors, preview length, and notification channels
- **Error Reporting**: Optional error channel for monitoring bot issues
- **JSON Persistence**: All settings saved locally and survive bot restarts

## Prerequisites

- Python 3.10 or higher
- A Discord bot token ([create one here](https://discord.com/developers/applications))
- Administrator permissions in your Discord server

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Jhn-git/forum-notifier-bot.git
   cd forum-notifier-bot
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your bot token:**

   Edit the `.env` file and add your bot token:
   ```env
   DISCORD_TOKEN=your_bot_token_here
   ```

4. **Invite the bot to your server:**

   Use this URL (replace `YOUR_CLIENT_ID` with your bot's client ID):
   ```
   https://discord.com/api/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=84992&scope=bot%20applications.commands
   ```

## Usage

1. **Start the bot:**
   ```bash
   python bot.py
   ```

2. **Configure the bot in Discord:**

   Run `/forum settings` to see all available options, then:
   - Set a notification channel: `/forum notifications #your-channel`
   - Add forums to monitor: `/forum monitor #your-forum`
   - (Optional) Set an error channel: `/forum errors #error-channel`

3. **Test the setup:**
   ```
   /forum test
   ```

The bot will now automatically post notifications when new threads are created in monitored forums.

## Commands

All commands require **Administrator** permission.

| Command | Parameters | Description |
|---------|-----------|-------------|
| `/forum monitor` | `channel` | Add a forum to the monitoring list |
| `/forum unmonitor` | `channel` | Remove a forum from monitoring |
| `/forum list` | — | Show all monitored forums |
| `/forum notifications` | `channel` | Set the channel for notifications |
| `/forum errors` | `channel` | Set the channel for error reports |
| `/forum color` | `hex_color` | Set embed color (e.g., #5865F2) |
| `/forum preview` | `length` | Set preview text length (1-500 characters) |
| `/forum settings` | — | Display all current settings |
| `/forum test` | — | Send a test notification |

## Configuration

Settings are stored in `data/settings.json`:

```json
{
  "notification_channel_id": null,
  "error_channel_id": null,
  "monitored_forums": [],
  "embed_color": "#2f3136",
  "preview_length": 100
}
```

You can modify these manually or use the slash commands.

## Notification Example

```
┌──────────────────────────────────────────────────┐
│ 📝 New Post in #help-forum                       │
├──────────────────────────────────────────────────┤
│ **How do I improve my aim?**                     │
│                                                  │
│ "I've been playing for a few months now and I   │
│ feel stuck around Gold rank..."                  │
│                                                  │
├──────────────────────────────────────────────────┤
│ 👤 Posted by                                     │
│ @Username                                        │
├──────────────────────────────────────────────────┤
│ Today at 3:45 PM                                 │
└──────────────────────────────────────────────────┘
  [ 🔗 Jump to Post ]  [ 📁 View Forum ]
```

## Project Structure

```
forum-notifier-bot/
├── bot.py                  # Entry point and bot initialization
├── cogs/
│   ├── forum_listener.py   # Event handler for thread creation
│   └── config_commands.py  # Slash command implementations
├── utils/
│   └── storage.py          # JSON read/write utilities
├── data/
│   └── settings.json       # Persistent configuration
├── requirements.txt        # Python dependencies
├── .env                    # Bot token (not committed)
└── README.md              # This file
```

## Required Bot Permissions

The bot needs the following permissions (included in the invite link):
- View Channels
- Send Messages
- Embed Links
- Use External Emojis

**Permission Integer:** `84992`

## Troubleshooting

**Bot not responding to commands:**
- Ensure the bot is online and has been invited with the correct permissions
- Check that commands have been synced (bot logs this on startup)

**Notifications not appearing:**
- Verify a notification channel is set using `/forum settings`
- Ensure the bot can view and send messages in the notification channel
- Check that forums are added to the monitoring list with `/forum list`

**Error: "DISCORD_TOKEN not found":**
- Make sure you've created a `.env` file with your bot token

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues or questions, please open an issue on GitHub.
