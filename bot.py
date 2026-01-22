import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
SERVER_ID = int(os.getenv('SERVER_ID'))


# Bot setup with necessary intents
intents = discord.Intents.default()
intents.members = True  # Fixed: needed for thread.owner mention


class ForumNotifierBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        """Called before on_ready. Load cogs and sync commands here."""
        # Load cogs
        cogs = ['cogs.forum_listener', 'cogs.config_commands']
        for cog in cogs:
            try:
                await self.load_extension(cog)
                print(f'Loaded {cog}')
            except Exception as e:
                print(f'Failed to load {cog}: {e}')

        # Sync slash commands
        try:
            synced = await self.tree.sync()
            print(f'Synced {len(synced)} command(s)')
        except Exception as e:
            print(f'Failed to sync commands: {e}')

    async def on_ready(self):
        """Called when bot is ready and connected."""
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')


bot = ForumNotifierBot()


def main():
    """Main entry point."""
    if not TOKEN:
        print("Error: DISCORD_TOKEN not found in .env file")
        return

    bot.run(TOKEN)


if __name__ == '__main__':
    main()