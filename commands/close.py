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
            await interaction.response.send_message("You are not the trainer for this ticket.", ephemeral=True)
            return
        database.increment_lessons(ticket_info["gamemode"], ticket_info["trainer_id"])
        await interaction.response.send_message("Closing ticket in 5 seconds...")
        await asyncio.sleep(5)
        gamemode = ticket_info["gamemode"]
        trainer_id = ticket_info["trainer_id"]
        customer_id = ticket_info["customer_id"]
        
        # Send DM to customer
        try:
            customer = await interaction.client.fetch_user(customer_id)
            trainer = await interaction.client.fetch_user(trainer_id)
            import sys, os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))
            import review_submission
            await customer.send(f"Your {gamemode} by {trainer.mention} lesson was completed.\n\nWould you like to submit a review?", view=review_submission.ReviewSubmissionView())
        except:
            pass
        
        message_id = database.get_panel_message_id(gamemode, trainer_id)
        if message_id:
            channel_name = config.channel_format.format(emoji=next((e for n, e in config.gamemodes if n == gamemode), ""), gamemode=gamemode)
            channel = next((c for c in interaction.guild.channels if c.name.lower() == channel_name.lower()), None)
            if channel:
                try:
                    msg = await channel.fetch_message(message_id)
                    data = database.get_panel_data(gamemode, trainer_id)
                    emoji = next((e for n, e in config.gamemodes if n == gamemode), "")
                    title = f"{emoji} {gamemode} Trainer - {data['ign']}" if emoji else f"{gamemode} Trainer - {data['ign']}"
                    price_text = f"**💸 Price: ${data['price']} USD**"
                    embed = discord.Embed(title=title, description=data['description'] + "\n\n" + price_text, color=data['colour'])
                    embed.set_thumbnail(url=f"https://render.crafty.gg/3d/bust/{data['ign']}")
                    embed.set_footer(text=f"{data['ign']} has completed {data['lessons']} lessons.")
                    import sys, os
                    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))
                    import purchase
                    await msg.edit(embed=embed, view=purchase.PurchaseView(active=data["active"]))
                except:
                    pass
        database.remove_ticket(interaction.channel.id)
        await interaction.channel.delete()

