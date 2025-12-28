import discord
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import config
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'data'))
import database

class ReviewSubmissionView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Submit a review", style=discord.ButtonStyle.primary, custom_id="submit_review_button")
    async def submit_review(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ReviewModal(interaction.message))

class ReviewModal(discord.ui.Modal, title="Submit Review"):
    def __init__(self, message):
        super().__init__()
        self.message = message
        self.rating_input = discord.ui.TextInput(label="Rating", placeholder="Enter 1, 2, 3, 4, or 5", required=True, max_length=1)
        self.add_item(self.rating_input)
        self.review_input = discord.ui.TextInput(label="Review", required=True, style=discord.TextStyle.paragraph, max_length=1000)
        self.add_item(self.review_input)

    async def on_submit(self, interaction: discord.Interaction):
        rating_value = self.rating_input.value.strip()
        if rating_value not in ['1', '2', '3', '4', '5']:
            await interaction.response.send_message("Invalid rating", ephemeral=True)
            return
        import re
        gamemode = re.search(r'Your (.+?) lesson by', self.message.content).group(1)
        trainer_id = int(re.search(r'<@(\d+)>', self.message.content).group(1))
        trainer_ign = database.get_trainer_ign(gamemode, trainer_id) or "Unknown"
        embed = discord.Embed(title=f"New {gamemode} review of {trainer_ign}!", description=f"{'⭐' * int(rating_value)}\n\n{self.review_input.value}")
        embed.set_thumbnail(url=f"https://render.crafty.gg/3d/bust/{trainer_ign}")
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        review_message = await next((c for c in interaction.client.get_guild(config.guild_id).channels if c.name.lower() == config.review_channel.lower()), None).send(embed=embed)
        await interaction.response.send_message(f"Review submitted ({review_message.jump_url})", ephemeral=True)
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Submit a review", style=discord.ButtonStyle.primary, disabled=True, custom_id="submit_review_button"))
        await self.message.edit(view=view)

async def setup(bot):
    bot.add_view(ReviewSubmissionView())

