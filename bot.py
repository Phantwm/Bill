import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import importlib

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    for filename in os.listdir('commands'):
        if filename.endswith('.py'):
            module = importlib.import_module(f'commands.{filename[:-3]}')
            await module.setup(bot)
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'commands'))
    import purchase
    await purchase.setup(bot)
    import reviews
    await reviews.setup(bot)
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} command(s)')
    except Exception as e:
        print(f'Failed to sync commands: {e}')

bot.run(os.getenv('DISCORD_TOKEN'))
