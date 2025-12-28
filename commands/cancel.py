import discord
from discord import app_commands
import asyncio

async def setup(bot):
    @bot.tree.command(name="cancel")
    async def cancel(interaction: discord.Interaction):
        await interaction.response.send_message("Closing ticket in 5 seconds...")
        await asyncio.sleep(5)
        await interaction.channel.delete()

