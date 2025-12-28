import discord
from discord import app_commands
import sys
import os
import asyncio
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import config
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'data'))
import database

async def setup(bot):
    @bot.tree.command(name="close")
    async def close(interaction: discord.Interaction):
        if not interaction.channel.category or interaction.channel.category.name.lower() != config.ticket_category.lower():
            await interaction.response.send_message("This is not a ticket.", ephemeral=True)
            return
        ticket_info = database.get_ticket_info(interaction.channel.id)
        if not ticket_info or ticket_info["trainer_id"] != interaction.user.id:
            await interaction.response.send_message("You are not the owner of this ticket.", ephemeral=True)
            return
        database.increment_lessons(ticket_info["gamemode"], ticket_info["trainer_id"])
        await interaction.response.send_message("Ticket closing in 5 seconds...")
        await asyncio.sleep(5)
        gamemode, trainer_id = ticket_info["gamemode"], ticket_info["trainer_id"]
        try:
            import sys, os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))
            import reviews
            trainer = await interaction.client.fetch_user(trainer_id)
            await (await interaction.client.fetch_user(ticket_info["customer_id"])).send(f"Your {gamemode} lesson by {trainer.mention} was completed.\n\nWould you like to submit a review?", view=reviews.ReviewSubmissionView())
        except:
            pass
        message_id = database.get_panel_message_id(gamemode, trainer_id)
        if message_id:
            emoji = next((e for n, e in config.gamemodes if n == gamemode), "")
            channel = next((c for c in interaction.guild.channels if c.name.lower() == config.channel_format.format(emoji=emoji, gamemode=gamemode).lower()), None)
            if channel:
                try:
                    import sys, os
                    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))
                    import purchase
                    data = database.get_panel_data(gamemode, trainer_id)
                    embed = discord.Embed(title=f"{emoji} {gamemode} Trainer - {data['ign']}" if emoji else f"{gamemode} Trainer - {data['ign']}", description=data['description'] + "\n\n" + f"**💸 Price: ${data['price']} USD**", color=data['colour'])
                    embed.set_thumbnail(url=f"https://render.crafty.gg/3d/bust/{data['ign']}")
                    embed.set_footer(text=f"{data['ign']} has completed {data['lessons']} lessons.")
                    await (await channel.fetch_message(message_id)).edit(embed=embed, view=purchase.PurchaseView(active=data["active"]))
                except:
                    pass
        database.remove_ticket(interaction.channel.id)
        await interaction.channel.delete()

