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
            await interaction.response.send_message("Invalid rating. Please enter 1, 2, 3, 4, or 5.", ephemeral=True)
            return
        
        rating = int(rating_value)
        review_text = self.review_input.value
        
        import re
        content = self.message.content
        gamemode_match = re.search(r'Your (.+?) by', content)
        trainer_mention_match = re.search(r'<@(\d+)>', content)
        
        if not gamemode_match or not trainer_mention_match:
            await interaction.response.send_message("Error: Could not parse review information.", ephemeral=True)
            return
        
        gamemode = gamemode_match.group(1)
        trainer_id = int(trainer_mention_match.group(1))
        
        database.add_trainer(gamemode, trainer_id)
        trainer_ign = database.get_trainer_ign(gamemode, trainer_id)
        if not trainer_ign:
            trainer_ign = "Unknown"
        
        stars = "⭐" * rating
        embed = discord.Embed(title=f"New {gamemode} review of {trainer_ign}!", description=f"{stars}\n\n{review_text}")
        embed.set_thumbnail(url=f"https://render.crafty.gg/3d/bust/{trainer_ign}")
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        
        guild = interaction.client.get_guild(config.guild_id)
        if not guild:
            await interaction.response.send_message("Error: Guild not found.", ephemeral=True)
            return
        
        channel = next((c for c in guild.channels if c.name.lower() == config.review_channel.lower()), None)
        if not channel:
            await interaction.response.send_message("Review channel not found.", ephemeral=True)
            return
        
        await channel.send(embed=embed)
        await interaction.response.send_message("Review submitted!", ephemeral=True)
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Submit a review", style=discord.ButtonStyle.primary, disabled=True, custom_id="submit_review_button"))
        await self.message.edit(view=view)

async def setup(bot):
    bot.add_view(ReviewSubmissionView())

