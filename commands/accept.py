import discord
import re
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import config
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))
import ticket

async def handle_accept(interaction: discord.Interaction, embed: discord.Embed):
    user_mention_match = re.search(r'<@(\d+)>', embed.description)
    gamemode_match = re.search(r'\*\*Gamemode:\*\* .+? (.+)', embed.description)
    if not user_mention_match or not gamemode_match:
        await interaction.followup.send("Error: Could not find user or gamemode.", ephemeral=True)
        return
    requester_id = int(user_mention_match.group(1))
    gamemode = gamemode_match.group(1)
    trainer_id = interaction.user.id
    
    trainer = await interaction.client.fetch_user(trainer_id)
    requester = await interaction.client.fetch_user(requester_id)
    
    guild = interaction.client.get_guild(config.guild_id)
    if not guild:
        await interaction.followup.send("Error: Guild not found.", ephemeral=True)
        return
    
    ticket_channel = await ticket.create_ticket(guild, gamemode, trainer, requester)
    if not ticket_channel:
        await interaction.followup.send("Error: Could not create ticket channel.", ephemeral=True)
        return
    
    message = f"Your {gamemode} training request has been accepted! ({ticket_channel.mention})"
    await requester.send(message)
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="Accept", style=discord.ButtonStyle.success, disabled=True, custom_id="accept_request"))
    view.add_item(discord.ui.Button(label="Deny", style=discord.ButtonStyle.danger, disabled=True, custom_id="deny_request"))
    await interaction.message.edit(view=view)
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'data'))
    import database
    trainer_ign = database.get_trainer_ign(gamemode, trainer_id)
    if not trainer_ign:
        trainer_ign = trainer.name
    ign_match = re.search(r'\*\*IGN:\*\* (.+)', embed.description)
    requester_ign = ign_match.group(1) if ign_match else requester.name
    ticket_embed = discord.Embed(title=f"{gamemode} Training Ticket", description=f"**Trainer:** {trainer.mention} ({trainer_ign})\n\n**Customer:** {requester.mention} ({requester_ign})")
    await ticket_channel.send(embed=ticket_embed)
    await interaction.followup.send(f"Request accepted. ({ticket_channel.mention})", ephemeral=True)

async def setup(bot):
    pass

