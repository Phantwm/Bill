import discord
from discord import app_commands
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'data'))
import database
import config

class PanelView(discord.ui.View):
    def __init__(self, gamemode, user_id, embed, active=True):
        super().__init__(timeout=None)
        self.gamemode = gamemode
        self.user_id = user_id
        self.embed = embed
        self.active = active

    @discord.ui.button(label="Set inactive", style=discord.ButtonStyle.primary, row=0)
    async def toggle_active(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            return
        new_active = database.toggle_active(self.gamemode, interaction.user.id)
        self.active = new_active
        button.label = "Set inactive" if new_active else "Set active"
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="Edit Description", style=discord.ButtonStyle.primary)
    async def edit_description(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            return
        data = database.get_panel_data(self.gamemode, interaction.user.id)
        current_description = data["description"] or ""
        await interaction.response.send_modal(DescriptionModal(self, current_description))

    @discord.ui.button(label="Edit Colour", style=discord.ButtonStyle.primary)
    async def edit_colour(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            return
        data = database.get_panel_data(self.gamemode, interaction.user.id)
        current_colour = f"#{data['colour']:06x}"
        await interaction.response.send_modal(ColourModal(self, current_colour))

    @discord.ui.button(label="Edit Price", style=discord.ButtonStyle.primary)
    async def edit_price(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            return
        data = database.get_panel_data(self.gamemode, interaction.user.id)
        current_price = data["price"]
        await interaction.response.send_modal(PriceModal(self, current_price))

    @discord.ui.button(label="Edit IGN", style=discord.ButtonStyle.primary)
    async def set_ign(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            return
        data = database.get_panel_data(self.gamemode, interaction.user.id)
        current_ign = data["ign"]
        await interaction.response.send_modal(IGNModal(self, current_ign))

    @discord.ui.button(label="Save", style=discord.ButtonStyle.success)
    async def save(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            return
        emoji = next((e for n, e in config.gamemodes if n == self.gamemode), "")
        channel_name = config.channel_format.format(emoji=emoji, gamemode=self.gamemode)
        channel = next((c for c in interaction.guild.channels if c.name.lower() == channel_name.lower()), None)
        if not channel:
            await interaction.response.send_message("Channel not found.", ephemeral=True)
            return
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))
        import purchase
        data = database.get_panel_data(self.gamemode, interaction.user.id)
        self.embed.set_footer(text=f"{data['ign']} has completed {data['lessons']} lessons.")
        purchase_view = purchase.PurchaseView(active=data["active"])
        message_id = database.get_panel_message_id(self.gamemode, interaction.user.id)
        if message_id:
            try:
                await (await channel.fetch_message(message_id)).edit(embed=self.embed, view=purchase_view)
                await interaction.response.edit_message(content="Panel updated.", embed=None, view=None)
            except:
                message_id = None
        if not message_id:
            msg = await channel.send(embed=self.embed, view=purchase_view)
            database.set_panel_message_id(self.gamemode, interaction.user.id, msg.id)
            await interaction.response.edit_message(content="Panel created.", embed=None, view=None)

class DescriptionModal(discord.ui.Modal, title="Edit Description"):
    def __init__(self, view, current_description):
        super().__init__()
        self.view = view
        self.description_input = discord.ui.TextInput(label="Edit Description", required=True, style=discord.TextStyle.paragraph, max_length=4000, default=current_description)
        self.add_item(self.description_input)

    async def on_submit(self, interaction: discord.Interaction):
        description = self.description_input.value
        database.set_panel_description(self.view.gamemode, interaction.user.id, description)
        data = database.get_panel_data(self.view.gamemode, interaction.user.id)
        price_text = f"**💸 Price: ${data['price']} USD**"
        self.view.embed.description = data['description'] + "\n\n" + price_text
        self.view.embed.set_footer(text=f"{data['ign']} has completed {data['lessons']} lessons.")
        await interaction.response.edit_message(embed=self.view.embed, view=self.view)

class PriceModal(discord.ui.Modal, title="Edit Price"):
    def __init__(self, view, current_price):
        super().__init__()
        self.view = view
        self.price_input = discord.ui.TextInput(label="Edit Price", required=False, max_length=100, default=current_price)
        self.add_item(self.price_input)

    async def on_submit(self, interaction: discord.Interaction):
        price_value = self.price_input.value.strip()
        if price_value and not price_value.isdigit():
            await interaction.response.send_message("Invalid price.", ephemeral=True)
            return
        database.set_panel_price(self.view.gamemode, interaction.user.id, price_value if price_value else None)
        data = database.get_panel_data(self.view.gamemode, interaction.user.id)
        price_text = f"**💸 Price: ${data['price']} USD**"
        self.view.embed.description = data['description'] + "\n\n" + price_text
        self.view.embed.set_footer(text=f"{data['ign']} has completed {data['lessons']} lessons.")
        await interaction.response.edit_message(embed=self.view.embed, view=self.view)

class ColourModal(discord.ui.Modal, title="Edit Colour"):
    def __init__(self, view, current_colour):
        super().__init__()
        self.view = view
        self.colour_input = discord.ui.TextInput(label="Edit Colour", required=True, max_length=7, default=current_colour)
        self.add_item(self.colour_input)

    async def on_submit(self, interaction: discord.Interaction):
        hex_value = self.colour_input.value.strip()
        if not hex_value.startswith('#') or len(hex_value) != 7 or not all(c in '0123456789ABCDEFabcdef' for c in hex_value[1:]):
            await interaction.response.send_message("Invalid colour.", ephemeral=True)
            return
        colour_int = int(hex_value[1:], 16)
        database.set_panel_colour(self.view.gamemode, interaction.user.id, colour_int)
        self.view.embed.color = colour_int
        data = database.get_panel_data(self.view.gamemode, interaction.user.id)
        self.view.embed.set_footer(text=f"{data['ign']} has completed {data['lessons']} lessons.")
        await interaction.response.edit_message(embed=self.view.embed, view=self.view)

class IGNModal(discord.ui.Modal, title="Edit IGN"):
    def __init__(self, view, current_ign):
        super().__init__()
        self.view = view
        self.ign_input = discord.ui.TextInput(label="Edit IGN", required=True, max_length=16, default=current_ign)
        self.add_item(self.ign_input)

    async def on_submit(self, interaction: discord.Interaction):
        ign = self.ign_input.value.strip()
        database.set_panel_ign(self.view.gamemode, interaction.user.id, ign)
        self.view.embed.set_thumbnail(url=f"https://render.crafty.gg/3d/bust/{ign}")
        emoji = next((e for n, e in config.gamemodes if n == self.view.gamemode), "")
        self.view.embed.title = f"{emoji} {self.view.gamemode} Trainer - {ign}" if emoji else f"{self.view.gamemode} Trainer - {ign}"
        data = database.get_panel_data(self.view.gamemode, interaction.user.id)
        self.view.embed.set_footer(text=f"{data['ign']} has completed {data['lessons']} lessons.")
        await interaction.response.edit_message(embed=self.view.embed, view=self.view)

async def setup(bot):
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))
    import purchase
    @bot.tree.command(name="panel")
    @app_commands.describe(gamemode="Gamemode")
    async def panel(interaction: discord.Interaction, gamemode: str):
        member = await interaction.guild.fetch_member(interaction.user.id)
        role_name = f"{gamemode} Trainer"
        role = discord.utils.get(interaction.guild.roles, name=role_name)
        if not role or role not in member.roles:
            await interaction.response.send_message("No permission.", ephemeral=True)
            return
        database.add_trainer(gamemode, interaction.user.id)
        data = database.get_panel_data(gamemode, interaction.user.id)
        emoji = next((e for n, e in config.gamemodes if n == gamemode), "")
        title = f"{emoji} {gamemode} Trainer - {data['ign']}" if emoji else f"{gamemode} Trainer - {data['ign']}"
        price_text = f"**💸 Price: ${data['price']} USD**"
        embed = discord.Embed(title=title, description=data['description'] + "\n\n" + price_text, color=data['colour'])
        embed.set_thumbnail(url=f"https://render.crafty.gg/3d/bust/{data['ign']}")
        embed.set_footer(text=f"{data['ign']} has completed {data['lessons']} lessons.")
        view = PanelView(gamemode, interaction.user.id, embed, data["active"])
        for child in view.children:
            if child == view.toggle_active:
                child.label = "Set inactive" if data["active"] else "Set active"
                break
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @panel.autocomplete('gamemode')
    async def gamemode_autocomplete(interaction: discord.Interaction, current: str):
        return [app_commands.Choice(name=f"{emoji} {name}" if emoji else name, value=name) for name, emoji in config.gamemodes if current.lower() in name.lower()]

