import discord
from discord import app_commands
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'data'))
import database
import config

class PurchaseView(discord.ui.View):
    def __init__(self, active=True):
        super().__init__(timeout=None)
        if not active:
            self.remove_item(next(c for c in list(self.children) if hasattr(c, 'custom_id') and c.custom_id == 'purchase_button'))
            self.add_item(discord.ui.Button(label="Inactive", style=discord.ButtonStyle.secondary, custom_id="purchase_button", disabled=True))

    @discord.ui.button(label="Purchase", style=discord.ButtonStyle.primary, custom_id="purchase_button")
    async def purchase(self, interaction: discord.Interaction, button: discord.ui.Button):
        trainer_info = database.get_trainer_by_message(interaction.message.id)
        if trainer_info["user_id"] == interaction.user.id:
            await interaction.response.send_message("You cannot purchase from yourself.", ephemeral=True)
            return
        await interaction.response.send_modal(PurchaseModal(trainer_info["user_id"], trainer_info["gamemode"]))

class PurchaseModal(discord.ui.Modal, title="Purchase Request"):
    def __init__(self, trainer_user_id, gamemode):
        super().__init__()
        self.trainer_user_id = trainer_user_id
        self.gamemode = gamemode
        self.ign_input = discord.ui.TextInput(label="Minecraft IGN", required=True, max_length=16)
        self.add_item(self.ign_input)
        self.timezone_input = discord.ui.TextInput(label="Timezone", required=True, max_length=50)
        self.add_item(self.timezone_input)
        self.payment_input = discord.ui.TextInput(label="Preferred Payment Method", required=True, max_length=100)
        self.add_item(self.payment_input)

    async def on_submit(self, interaction: discord.Interaction):
        trainer = await interaction.client.fetch_user(self.trainer_user_id)
        await interaction.response.send_message(f"Requested training from {trainer.mention}.", ephemeral=True)
        emoji = next((e for n, e in config.gamemodes if n == self.gamemode), "")
        description = f"**Gamemode:** {emoji} {self.gamemode}\n\n**User:** {interaction.user.mention}\n\n**IGN:** {self.ign_input.value}\n\n**Timezone:** {self.timezone_input.value}\n\n**Preferred Payment Method:** {self.payment_input.value}"
        embed = discord.Embed(title="You have a new training request!", description=description)
        view = RequestResponseView()
        await trainer.send(embed=embed, view=view)

class RequestResponseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.success, custom_id="accept_request")
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        [setattr(i, 'disabled', True) for i in self.children]
        await interaction.message.edit(view=self)
        import sys, os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))
        import accept
        await accept.handle_accept(interaction, interaction.message.embeds[0])

    @discord.ui.button(label="Deny", style=discord.ButtonStyle.danger, custom_id="deny_request")
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        import sys, os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))
        import deny
        await interaction.response.send_modal(deny.DenyModal(interaction.message.embeds[0], interaction.message, self))

async def setup(bot):
    bot.add_view(PurchaseView())
    bot.add_view(RequestResponseView())

