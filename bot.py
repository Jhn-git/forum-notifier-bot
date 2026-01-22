import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Bot setup with necessary intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    """Called when bot is ready and connected."""
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

    # Load cogs
    await load_cogs()

    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} command(s)')
    except Exception as e:
        print(f'Failed to sync commands: {e}')


async def load_cogs():
    """Load all cogs from the cogs directory."""
    cogs = ['cogs.forum_listener', 'cogs.config_commands']
    for cog in cogs:
        try:
            await bot.load_extension(cog)
            print(f'Loaded {cog}')
        except Exception as e:
            print(f'Failed to load {cog}: {e}')


def main():
    """Main entry point."""
    if not TOKEN:
        print("Error: DISCORD_TOKEN not found in .env file")
        return

    bot.run(TOKEN)


if __name__ == '__main__':
    main()
