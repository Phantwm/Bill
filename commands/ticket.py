import discord
import config
import re
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'data'))
import database


async def create_ticket(guild: discord.Guild, gamemode: str, trainer: discord.User, requester: discord.User):
    category = next((c for c in guild.categories if c.name.lower() == config.ticket_category.lower()), None)
    if not category:
        return None
    
    try:
        trainer_member = await guild.fetch_member(trainer.id)
        requester_member = await guild.fetch_member(requester.id)
    except:
        return None
    
    channel_name = f"{re.sub(r'[^a-z0-9-]', '', gamemode.lower())[:20] or 'user'}-{re.sub(r'[^a-z0-9-]', '', trainer.name.lower())[:20] or 'user'}-{re.sub(r'[^a-z0-9-]', '', requester.name.lower())[:20] or 'user'}"[:100]
    
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        trainer_member: discord.PermissionOverwrite(view_channel=True),
        requester_member: discord.PermissionOverwrite(view_channel=True)
    }
    
    channel = await guild.create_text_channel(channel_name, category=category, overwrites=overwrites)
    database.add_ticket(channel.id, trainer.id, requester.id, gamemode)
    return channel

async def setup(bot):
    pass

