import discord
from discord.ext import commands
import datetime
from utils.storage import load_settings, save_settings


class ForumListener(commands.Cog):
    """Listens for new forum posts and sends notifications."""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_thread_create(self, thread: discord.Thread):
        """Handle new thread creation in monitored forums."""
        settings = load_settings()

        # Check if thread is in a monitored forum
        if thread.parent_id not in settings['monitored_forums']:
            return

        # Check if this is a newly created thread (not archived/unarchived)
        # Threads created more than 10 seconds ago are likely unarchived, not new
        now = datetime.datetime.now(datetime.timezone.utc)
        age = (now - thread.created_at).total_seconds()

        if age > 10:
            return  # Skip old/unarchived threads

        # Check if notification channel is set
        notification_channel_id = settings['notification_channel_id']
        if not notification_channel_id:
            print(f"Warning: New post in {thread.parent.name} but no notification channel set")
            return

        # Get notification channel
        try:
            notification_channel = self.bot.get_channel(notification_channel_id)
            if not notification_channel:
                notification_channel = await self.bot.fetch_channel(notification_channel_id)
        except discord.NotFound:
            await self._handle_error(
                settings,
                f"Notification channel (ID: {notification_channel_id}) not found or deleted"
            )
            return
        except discord.Forbidden:
            await self._handle_error(
                settings,
                f"Missing permissions to access notification channel (ID: {notification_channel_id})"
            )
            return

        # Build and send notification
        try:
            embed = await self._build_embed(thread, settings)
            view = self._build_buttons(thread)
            await notification_channel.send(embed=embed, view=view)
        except Exception as e:
            await self._handle_error(
                settings,
                f"Failed to send notification for post in {thread.parent.name}: {str(e)}"
            )

    async def _build_embed(self, thread: discord.Thread, settings: dict) -> discord.Embed:
        """Build the notification embed."""
        # Get preview text from the first message
        preview_text = ""
        starter_message = None
        try:
            # Fetch the starter message
            starter_message = thread.starter_message
            if not starter_message:
                # If not cached, fetch it
                async for message in thread.history(limit=1, oldest_first=True):
                    starter_message = message
                    break

            if starter_message and starter_message.content:
                preview_length = settings['preview_length']
                content = starter_message.content.strip()
                if len(content) > preview_length:
                    preview_text = f'"{content[:preview_length]}..."'
                else:
                    preview_text = f'"{content}"'
        except Exception as e:
            print(f"Error fetching thread starter message: {e}")
            preview_text = ""

        # Extract attachment info
        media_type, media_url, has_video = self._get_media_info(starter_message)

        # Get forum name
        forum_name = thread.parent.name if thread.parent else "Unknown Forum"

        # Extract tag names
        tag_names = self._get_tag_names(thread)

        # Build description with sections
        description_parts = []
        if preview_text:
            description_parts.append(preview_text)
        if tag_names:
            description_parts.append(f"🏷️ {' • '.join(tag_names)}")
        if has_video:
            description_parts.append("🎬 Video attached")

        description = "\n".join(description_parts) if description_parts else ""

        # Build embed with clickable title
        embed = discord.Embed(
            title=thread.name,
            url=thread.jump_url,
            description=description,
            color=int(settings['embed_color'].replace('#', ''), 16),
            timestamp=discord.utils.utcnow()
        )

        # Add footer
        embed.set_footer(text=f"Posted in #{forum_name}")

        # Add avatar thumbnail
        if thread.owner:
            try:
                embed.set_thumbnail(url=thread.owner.display_avatar.url)
            except Exception as e:
                print(f"Error setting avatar: {e}")

        # Add author field
        if thread.owner:
            embed.add_field(
                name="👤 Posted by",
                value=thread.owner.mention,
                inline=False
            )

        # Add media image
        if media_url:
            try:
                embed.set_image(url=media_url)
            except Exception as e:
                print(f"Error setting media image: {e}")

        return embed

    def _build_buttons(self, thread: discord.Thread) -> discord.ui.View:
        """Build the button view with link buttons."""
        view = discord.ui.View()

        # View Forum button
        if thread.parent:
            forum_url = f"https://discord.com/channels/{thread.guild.id}/{thread.parent_id}"
            view.add_item(
                discord.ui.Button(
                    label="📁 View Forum",
                    url=forum_url,
                    style=discord.ButtonStyle.link
                )
            )

        return view

    def _get_media_info(self, starter_message) -> tuple:
        """Extract media attachment information from starter message.

        Returns:
            tuple: (media_type, media_url, has_video)
                - media_type: 'image', 'video', or None
                - media_url: attachment URL or None
                - has_video: Boolean indicating if video is present
        """
        try:
            if not starter_message or not starter_message.attachments:
                return (None, None, False)

            for attachment in starter_message.attachments:
                content_type = attachment.content_type
                if not content_type:
                    continue

                if content_type.startswith('image/'):
                    return ('image', attachment.url, False)
                elif content_type.startswith('video/'):
                    return ('video', attachment.url, True)

            return (None, None, False)
        except Exception as e:
            print(f"Error getting media info: {e}")
            return (None, None, False)

    def _get_tag_names(self, thread: discord.Thread) -> list:
        """Resolve thread tag IDs to tag names.

        Returns:
            list: List of tag names applied to the thread
        """
        try:
            if not hasattr(thread, 'applied_tags') or not thread.applied_tags:
                return []

            if not thread.parent or not hasattr(thread.parent, 'available_tags'):
                return []

            # Build tag lookup dictionary
            tag_lookup = {tag.id: tag.name for tag in thread.parent.available_tags}

            # Resolve tag IDs to names
            tag_names = []
            for tag in thread.applied_tags:
                if tag.id in tag_lookup:
                    tag_names.append(tag_lookup[tag.id])

            return tag_names
        except Exception as e:
            print(f"Error getting tag names: {e}")
            return []

    async def _handle_error(self, settings: dict, error_message: str):
        """Handle and report errors."""
        print(f"Error: {error_message}")

        # Try to send to error channel if configured
        error_channel_id = settings['error_channel_id']
        if error_channel_id:
            try:
                error_channel = self.bot.get_channel(error_channel_id)
                if not error_channel:
                    error_channel = await self.bot.fetch_channel(error_channel_id)

                embed = discord.Embed(
                    title="⚠️ Forum Notifier Error",
                    description=error_message,
                    color=0xFF0000,
                    timestamp=discord.utils.utcnow()
                )
                await error_channel.send(embed=embed)
            except Exception as e:
                print(f"Failed to send error to error channel: {e}")


async def setup(bot):
    """Setup function for loading the cog."""
    await bot.add_cog(ForumListener(bot))
