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
        for item in self.view.children:
            item.disabled = True
        await self.message.edit(view=self.view)
        user_mention_match = re.search(r'<@(\d+)>', self.embed.description)
        gamemode_match = re.search(r'\*\*Gamemode:\*\* .+? (.+)', self.embed.description)
        if not user_mention_match or not gamemode_match:
            await interaction.followup.send("Error: Could not find user or gamemode.", ephemeral=True)
            return
        requester_id = int(user_mention_match.group(1))
        gamemode = gamemode_match.group(1)
        requester = await interaction.client.fetch_user(requester_id)
        message = f"Your {gamemode} training request has been denied.\n\nReason: {self.reason_input.value}"
        await requester.send(message)
        await interaction.followup.send("Request denied.", ephemeral=True)

async def setup(bot):
    pass

