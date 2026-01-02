import discord
from discord import app_commands
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'data'))
import database
import config

class AdminPanelView(discord.ui.View):
    def __init__(self, gamemode, user_id, embed, active=True):
        super().__init__(timeout=None)
        self.gamemode = gamemode
        self.user_id = user_id
        self.embed = embed
        self.active = active

    @discord.ui.button(label="Set inactive", style=discord.ButtonStyle.primary, row=0)
    async def toggle_active(self, interaction: discord.Interaction, button: discord.ui.Button):
        member = await interaction.guild.fetch_member(interaction.user.id)
        if interaction.user.id != self.user_id and not any(r.name == "Owner" for r in member.roles):
            return
        new_active = database.toggle_active(self.gamemode, self.user_id)
        self.active = new_active
        button.label = "Set inactive" if new_active else "Set active"
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="Edit Description", style=discord.ButtonStyle.primary)
    async def edit_description(self, interaction: discord.Interaction, button: discord.ui.Button):
        member = await interaction.guild.fetch_member(interaction.user.id)
        if interaction.user.id != self.user_id and not any(r.name == "Owner" for r in member.roles):
            return
        await interaction.response.send_modal(AdminDescriptionModal(self, database.get_panel_data(self.gamemode, self.user_id)["description"] or ""))

    @discord.ui.button(label="Edit Colour", style=discord.ButtonStyle.primary)
    async def edit_colour(self, interaction: discord.Interaction, button: discord.ui.Button):
        member = await interaction.guild.fetch_member(interaction.user.id)
        if interaction.user.id != self.user_id and not any(r.name == "Owner" for r in member.roles):
            return
        await interaction.response.send_modal(AdminColourModal(self, f"#{database.get_panel_data(self.gamemode, self.user_id)['colour']:06x}"))

    @discord.ui.button(label="Edit Price", style=discord.ButtonStyle.primary)
    async def edit_price(self, interaction: discord.Interaction, button: discord.ui.Button):
        member = await interaction.guild.fetch_member(interaction.user.id)
        if interaction.user.id != self.user_id and not any(r.name == "Owner" for r in member.roles):
            return
        await interaction.response.send_modal(AdminPriceModal(self, database.get_panel_data(self.gamemode, self.user_id)["price"]))

    @discord.ui.button(label="Edit IGN", style=discord.ButtonStyle.primary)
    async def set_ign(self, interaction: discord.Interaction, button: discord.ui.Button):
        member = await interaction.guild.fetch_member(interaction.user.id)
        if interaction.user.id != self.user_id and not any(r.name == "Owner" for r in member.roles):
            return
        await interaction.response.send_modal(AdminIGNModal(self, database.get_panel_data(self.gamemode, self.user_id)["ign"]))

    @discord.ui.button(label="Save", style=discord.ButtonStyle.success)
    async def save(self, interaction: discord.Interaction, button: discord.ui.Button):
        member = await interaction.guild.fetch_member(interaction.user.id)
        if interaction.user.id != self.user_id and not any(r.name == "Owner" for r in member.roles):
            return
        emoji = next((e for n, e in config.gamemodes if n == self.gamemode), "")
        channel = next((c for c in interaction.guild.channels if c.name.lower() == config.channel_format.format(emoji=emoji, gamemode=self.gamemode).lower()), None)
        import sys, os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))
        import purchase
        data = database.get_panel_data(self.gamemode, self.user_id)
        self.embed.set_footer(text=f"{data['ign']} has completed {data['lessons']} lessons.")
        view = purchase.PurchaseView(active=data["active"])
        message_id = database.get_panel_message_id(self.gamemode, self.user_id)
        try:
            if message_id:
                await (await channel.fetch_message(message_id)).edit(embed=self.embed, view=view)
                await interaction.response.edit_message(content="Panel updated.", embed=None, view=None)
            else:
                raise
        except:
            database.set_panel_message_id(self.gamemode, self.user_id, (await channel.send(embed=self.embed, view=view)).id)
            await interaction.response.edit_message(content="Panel created.", embed=None, view=None)

class AdminDescriptionModal(discord.ui.Modal, title="Edit Description"):
    def __init__(self, view, current_description):
        super().__init__()
        self.view = view
        self.description_input = discord.ui.TextInput(label="Edit Description", required=True, style=discord.TextStyle.paragraph, max_length=4000, default=current_description)
        self.add_item(self.description_input)

    async def on_submit(self, interaction: discord.Interaction):
        database.set_panel_description(self.view.gamemode, self.view.user_id, self.description_input.value)
        data = database.get_panel_data(self.view.gamemode, self.view.user_id)
        self.view.embed.description = data['description'] + "\n\n" + f"**💸 Price: ${data['price']} USD**"
        self.view.embed.set_footer(text=f"{data['ign']} has completed {data['lessons']} lessons.")
        await interaction.response.edit_message(embed=self.view.embed, view=self.view)

class AdminPriceModal(discord.ui.Modal, title="Edit Price"):
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
        database.set_panel_price(self.view.gamemode, self.view.user_id, price_value if price_value else None)
        data = database.get_panel_data(self.view.gamemode, self.view.user_id)
        self.view.embed.description = data['description'] + "\n\n" + f"**💸 Price: ${data['price']} USD**"
        self.view.embed.set_footer(text=f"{data['ign']} has completed {data['lessons']} lessons.")
        await interaction.response.edit_message(embed=self.view.embed, view=self.view)

class AdminColourModal(discord.ui.Modal, title="Edit Colour"):
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
        database.set_panel_colour(self.view.gamemode, self.view.user_id, colour_int)
        self.view.embed.color = colour_int
        data = database.get_panel_data(self.view.gamemode, self.view.user_id)
        self.view.embed.set_footer(text=f"{data['ign']} has completed {data['lessons']} lessons.")
        await interaction.response.edit_message(embed=self.view.embed, view=self.view)

class AdminIGNModal(discord.ui.Modal, title="Edit IGN"):
    def __init__(self, view, current_ign):
        super().__init__()
        self.view = view
        self.ign_input = discord.ui.TextInput(label="Edit IGN", required=True, max_length=16, default=current_ign)
        self.add_item(self.ign_input)

    async def on_submit(self, interaction: discord.Interaction):
        from urllib.parse import quote
        ign = self.ign_input.value.strip()
        database.set_panel_ign(self.view.gamemode, self.view.user_id, ign)
        self.view.embed.set_thumbnail(url=f"https://render.crafty.gg/3d/bust/{quote(ign)}")
        emoji = next((e for n, e in config.gamemodes if n == self.view.gamemode), "")
        self.view.embed.title = f"{emoji} {self.view.gamemode} Trainer - {ign}" if emoji else f"{self.view.gamemode} Trainer - {ign}"
        data = database.get_panel_data(self.view.gamemode, self.view.user_id)
        self.view.embed.set_footer(text=f"{data['ign']} has completed {data['lessons']} lessons.")
        await interaction.response.edit_message(embed=self.view.embed, view=self.view)

async def setup(bot):
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))
    import purchase
    @bot.tree.command(name="adminpanel")
    @app_commands.describe(gamemode="Gamemode", user="User")
    async def adminpanel(interaction: discord.Interaction, gamemode: str, user: discord.User):
        member = await interaction.guild.fetch_member(interaction.user.id)
        if not any(r.name == "Owner" for r in member.roles):
            await interaction.response.send_message("No permission.", ephemeral=True)
            return
        from urllib.parse import quote
        database.add_trainer(gamemode, user.id)
        data = database.get_panel_data(gamemode, user.id)
        emoji = next((e for n, e in config.gamemodes if n == gamemode), "")
        embed = discord.Embed(title=f"{emoji} {gamemode} Trainer - {data['ign']}" if emoji else f"{gamemode} Trainer - {data['ign']}", description=data['description'] + "\n\n" + f"**💸 Price: ${data['price']} USD**", color=data['colour'])
        embed.set_thumbnail(url=f"https://render.crafty.gg/3d/bust/{quote(data['ign'])}")
        embed.set_footer(text=f"{data['ign']} has completed {data['lessons']} lessons.")
        view = AdminPanelView(gamemode, user.id, embed, data["active"])
        [setattr(c, 'label', "Set inactive" if data["active"] else "Set active") for c in view.children if c == view.toggle_active]
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @adminpanel.autocomplete('gamemode')
    async def gamemode_autocomplete(interaction: discord.Interaction, current: str):
        return [app_commands.Choice(name=f"{emoji} {name}" if emoji else name, value=name) for name, emoji in config.gamemodes if current.lower() in name.lower()]

