import discord
import re

class DenyModal(discord.ui.Modal, title="Deny Request"):
    def __init__(self, embed, message, view):
        super().__init__()
        self.embed = embed
        self.message = message
        self.view = view
        self.reason_input = discord.ui.TextInput(label="Reason", required=True, style=discord.TextStyle.paragraph, max_length=1000)
        self.add_item(self.reason_input)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        [setattr(i, 'disabled', True) for i in self.view.children]
        await self.message.edit(view=self.view)
        requester_id = int(re.search(r'<@(\d+)>', self.embed.description).group(1))
        gamemode = re.search(r'\*\*Gamemode:\*\* .+? (.+)', self.embed.description).group(1)
        await (await interaction.client.fetch_user(requester_id)).send(f"Your {gamemode} training request has been denied.\n\nReason: {self.reason_input.value}")
        await interaction.followup.send("Request denied.", ephemeral=True)

async def setup(bot):
    pass

