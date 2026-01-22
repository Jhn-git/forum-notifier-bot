import discord
from discord import app_commands
from discord.ext import commands
from utils.storage import load_settings, save_settings


class ConfigCommands(commands.GroupCog, name="forum", description="Forum notifier configuration"):
    """Slash commands for configuring the forum notifier bot."""

    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    @app_commands.command(name="monitor", description="Add a forum channel to the monitoring list")
    @app_commands.describe(channel="The forum channel to monitor")
    @app_commands.default_permissions(administrator=True)
    async def monitor(self, interaction: discord.Interaction, channel: discord.ForumChannel):
        """Add a forum to the watch list."""
        settings = load_settings()

        if channel.id in settings['monitored_forums']:
            await interaction.response.send_message(
                f"❌ {channel.mention} is already being monitored.",
                ephemeral=True
            )
            return

        settings['monitored_forums'].append(channel.id)
        save_settings(settings)

        await interaction.response.send_message(
            f"✅ Now monitoring {channel.mention} for new posts.",
            ephemeral=True
        )

    @app_commands.command(name="unmonitor", description="Remove a forum channel from the monitoring list")
    @app_commands.describe(channel="The forum channel to stop monitoring")
    @app_commands.default_permissions(administrator=True)
    async def unmonitor(self, interaction: discord.Interaction, channel: discord.ForumChannel):
        """Remove a forum from monitoring."""
        settings = load_settings()

        if channel.id not in settings['monitored_forums']:
            await interaction.response.send_message(
                f"❌ {channel.mention} is not currently being monitored.",
                ephemeral=True
            )
            return

        settings['monitored_forums'].remove(channel.id)
        save_settings(settings)

        await interaction.response.send_message(
            f"✅ Stopped monitoring {channel.mention}.",
            ephemeral=True
        )

    @app_commands.command(name="list", description="Show all monitored forum channels")
    @app_commands.default_permissions(administrator=True)
    async def list_forums(self, interaction: discord.Interaction):
        """Show all monitored forums."""
        settings = load_settings()

        if not settings['monitored_forums']:
            await interaction.response.send_message(
                "📋 No forums are currently being monitored.",
                ephemeral=True
            )
            return

        # Build list of monitored forums
        forum_list = []
        for forum_id in settings['monitored_forums']:
            channel = interaction.guild.get_channel(forum_id)
            if channel:
                forum_list.append(f"• {channel.mention}")
            else:
                forum_list.append(f"• Unknown Forum (ID: {forum_id})")

        embed = discord.Embed(
            title="📋 Monitored Forums",
            description="\n".join(forum_list),
            color=0x2f3136
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="notifications", description="Set the channel for post notifications")
    @app_commands.describe(channel="The channel where notifications will be sent")
    @app_commands.default_permissions(administrator=True)
    async def notifications(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """Set notification channel."""
        settings = load_settings()
        settings['notification_channel_id'] = channel.id
        save_settings(settings)

        await interaction.response.send_message(
            f"✅ Notifications will now be sent to {channel.mention}.",
            ephemeral=True
        )

    @app_commands.command(name="errors", description="Set the channel for error reports")
    @app_commands.describe(channel="The channel where errors will be reported")
    @app_commands.default_permissions(administrator=True)
    async def errors(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """Set error reporting channel."""
        settings = load_settings()
        settings['error_channel_id'] = channel.id
        save_settings(settings)

        await interaction.response.send_message(
            f"✅ Errors will now be reported to {channel.mention}.",
            ephemeral=True
        )

    @app_commands.command(name="color", description="Set the embed color for notifications")
    @app_commands.describe(hex_color="Hex color code (e.g., #5865F2)")
    @app_commands.default_permissions(administrator=True)
    async def color(self, interaction: discord.Interaction, hex_color: str):
        """Set embed color."""
        # Validate hex color
        hex_color = hex_color.strip()
        if not hex_color.startswith('#'):
            hex_color = '#' + hex_color

        if len(hex_color) != 7:
            await interaction.response.send_message(
                "❌ Invalid hex color. Please use format: #RRGGBB (e.g., #5865F2)",
                ephemeral=True
            )
            return

        try:
            int(hex_color.replace('#', ''), 16)
        except ValueError:
            await interaction.response.send_message(
                "❌ Invalid hex color. Please use format: #RRGGBB (e.g., #5865F2)",
                ephemeral=True
            )
            return

        settings = load_settings()
        settings['embed_color'] = hex_color
        save_settings(settings)

        # Show preview
        embed = discord.Embed(
            title="✅ Embed color updated",
            description=f"New color: {hex_color}",
            color=int(hex_color.replace('#', ''), 16)
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="preview", description="Set the preview text length for notifications")
    @app_commands.describe(length="Number of characters to preview (1-500)")
    @app_commands.default_permissions(administrator=True)
    async def preview(self, interaction: discord.Interaction, length: int):
        """Set preview character count."""
        if length < 1 or length > 500:
            await interaction.response.send_message(
                "❌ Preview length must be between 1 and 500 characters.",
                ephemeral=True
            )
            return

        settings = load_settings()
        settings['preview_length'] = length
        save_settings(settings)

        await interaction.response.send_message(
            f"✅ Preview length set to {length} characters.",
            ephemeral=True
        )

    @app_commands.command(name="settings", description="Display all current settings")
    @app_commands.default_permissions(administrator=True)
    async def settings_display(self, interaction: discord.Interaction):
        """Display all current settings."""
        settings = load_settings()

        # Build settings display
        notification_channel = interaction.guild.get_channel(settings['notification_channel_id'])
        notification_text = notification_channel.mention if notification_channel else "Not set"

        error_channel = interaction.guild.get_channel(settings['error_channel_id'])
        error_text = error_channel.mention if error_channel else "Not set"

        monitored_count = len(settings['monitored_forums'])

        embed = discord.Embed(
            title="⚙️ Forum Notifier Settings",
            color=int(settings['embed_color'].replace('#', ''), 16)
        )

        embed.add_field(
            name="📢 Notification Channel",
            value=notification_text,
            inline=False
        )

        embed.add_field(
            name="⚠️ Error Channel",
            value=error_text,
            inline=False
        )

        embed.add_field(
            name="📋 Monitored Forums",
            value=f"{monitored_count} forum(s)",
            inline=True
        )

        embed.add_field(
            name="🎨 Embed Color",
            value=settings['embed_color'],
            inline=True
        )

        embed.add_field(
            name="📏 Preview Length",
            value=f"{settings['preview_length']} characters",
            inline=True
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="test", description="Send a test notification")
    @app_commands.default_permissions(administrator=True)
    async def test(self, interaction: discord.Interaction):
        """Send a test notification."""
        settings = load_settings()

        notification_channel_id = settings['notification_channel_id']
        if not notification_channel_id:
            await interaction.response.send_message(
                "❌ No notification channel set. Use `/forum notifications` first.",
                ephemeral=True
            )
            return

        try:
            notification_channel = interaction.guild.get_channel(notification_channel_id)
            if not notification_channel:
                notification_channel = await interaction.guild.fetch_channel(notification_channel_id)

            # Build test embed
            embed = discord.Embed(
                title="📝 New Post in #test-forum",
                description="**Test Post Title**\n\n\"This is a test notification to verify the bot is working correctly...\"",
                color=int(settings['embed_color'].replace('#', ''), 16),
                timestamp=discord.utils.utcnow()
            )

            embed.add_field(
                name="👤 Posted by",
                value=interaction.user.mention,
                inline=False
            )

            # Build test buttons
            view = discord.ui.View()
            view.add_item(
                discord.ui.Button(
                    label="🔗 Jump to Post",
                    url="https://discord.com",
                    style=discord.ButtonStyle.link
                )
            )
            view.add_item(
                discord.ui.Button(
                    label="📁 View Forum",
                    url="https://discord.com",
                    style=discord.ButtonStyle.link
                )
            )

            await notification_channel.send(embed=embed, view=view)
            await interaction.response.send_message(
                f"✅ Test notification sent to {notification_channel.mention}.",
                ephemeral=True
            )

        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ Missing permissions to send messages to the notification channel.",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Failed to send test notification: {str(e)}",
                ephemeral=True
            )


async def setup(bot):
    """Setup function for loading the cog."""
    await bot.add_cog(ConfigCommands(bot))
