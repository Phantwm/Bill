import discord
import re
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import config
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))
import ticket

async def handle_accept(interaction: discord.Interaction, embed: discord.Embed):
    requester_id = int(re.search(r'<@(\d+)>', embed.description).group(1))
    gamemode = re.search(r'\*\*Gamemode:\*\* .+? (.+)', embed.description).group(1)
    trainer_id = interaction.user.id
    trainer = await interaction.client.fetch_user(trainer_id)
    requester = await interaction.client.fetch_user(requester_id)
    ticket_channel = await ticket.create_ticket(interaction.client.get_guild(config.guild_id), gamemode, trainer, requester)
    await requester.send(f"Your {gamemode} training request has been accepted. ({ticket_channel.mention})")
    view = discord.ui.View()
    [view.add_item(discord.ui.Button(label=l, style=s, disabled=True, custom_id=c)) for l, s, c in [("Accept", discord.ButtonStyle.success, "accept_request"), ("Deny", discord.ButtonStyle.danger, "deny_request")]]
    await interaction.message.edit(view=view)
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'data'))
    import database
    ign_match = re.search(r'\*\*IGN:\*\* (.+)', embed.description)
    await ticket_channel.send(embed=discord.Embed(title=f"{gamemode} Training Ticket", description=f"**Trainer:** {trainer.mention} ({database.get_trainer_ign(gamemode, trainer_id) or trainer.name})\n\n**Customer:** {requester.mention} ({ign_match.group(1) if ign_match else requester.name})"))
    await interaction.followup.send(f"Request accepted. ({ticket_channel.mention})", ephemeral=True)

async def setup(bot):
    pass

