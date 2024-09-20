import os
import random
import string
import discord
import asyncio
from discord import app_commands
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont, ImageFilter


class VerificationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.verification_channel_id = None
        self.verification_header = None
        self.verification_description = None
        self.verification_role_id = None

    
    def generate_captcha_image(self, for_user):

        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        width, height = 200, 100

        background_color = (random.randint(200, 255), random.randint(200, 255), random.randint(200, 255))  # Light colors
        image = Image.new('RGB', (width, height), background_color)
        draw = ImageDraw.Draw(image)

        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except IOError:
            font = ImageFont.load_default()

        for _ in range(8):  
            start_point = (random.randint(0, width), random.randint(0, height))
            end_point = (random.randint(0, width), random.randint(0, height))
            line_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))  # Random line color
            draw.line([start_point, end_point], fill=line_color, width=2)

        for i, char in enumerate(code):

            char_x = 10 + i * 30 + random.randint(-5, 5)
            char_y = random.randint(10, 40)

            text_color = (random.randint(0, 150), random.randint(0, 150), random.randint(0, 150))  # Dark colors

            char_image = Image.new('RGBA', (40, 40), (255, 255, 255, 0))
            char_draw = ImageDraw.Draw(char_image)
            char_draw.text((0, 0), char, font=font, fill=text_color)
            char_image = char_image.rotate(random.randint(-30, 30), expand=1)

            image.paste(char_image, (char_x, char_y), char_image)

        image = image.filter(ImageFilter.GaussianBlur(1))

        directory = 'data/images/captcha/'
        os.makedirs(directory, exist_ok=True)

        image_path = f'{directory}{for_user}_captcha.png'
        image.save(image_path)

        return code, image_path


    verification_group = app_commands.Group(name="verification", description="Set up verification method.")

    @verification_group.command(name="setup", description="Set up the verification channel, message, and role.")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_verification(self, interaction: discord.Interaction, 
                                 channel: discord.TextChannel,
                                 header: str,
                                 description: str,
                                 role: discord.Role = None):

        self.verification_channel_id = channel.id
        self.verification_header = header
        self.verification_description = description
        self.verification_role_id = role.id if role else None

        #verification embed
        embed = discord.Embed(title=self.verification_header, description=self.verification_description, color=discord.Color.blue())
        button = discord.ui.Button(label="Verify", style=discord.ButtonStyle.green)
        
        view = discord.ui.View()
        view.add_item(button)

        #callback
        async def on_button_click(interaction: discord.Interaction):
            user = interaction.user
            guild = interaction.guild

            await interaction.response.defer(ephemeral=True)

            # Check if verification role is set and if the user already has it
            if self.verification_role_id:
                role = guild.get_role(self.verification_role_id)
                if role in user.roles:
                    # If user already has the role
                    await interaction.followup.send("You are already verified!", ephemeral=True)
                    return

            user_id = user.id
            user_captcha_code, user_captcha_path = self.generate_captcha_image(user_id)

            # Send image in DMs
            try:
                await interaction.followup.send("Please solve the CAPTCHA sent by me on your DM.", ephemeral=True)
                with open(user_captcha_path, 'rb') as file:
                    captcha_file = discord.File(file)

                    embed = discord.Embed(
                        title="Please solve the CAPTCHA to verify. Type the code shown in the image below.",
                        color=discord.Color.purple()
                    )
                    
                    await user.send(embed=embed)
                    await user.send(file=captcha_file)
                os.remove(user_captcha_path)

            except discord.errors.Forbidden:
                await interaction.followup.send("Couldn't send you a DM. Please enable DMs and try again.", ephemeral=True)
                return
            except Exception as e:
                await interaction.followup.send("An error occurred while sending the CAPTCHA. Please try again.", ephemeral=True)
                return

            # check the response from the user
            def check(message: discord.Message):
                return message.author == user and message.guild is None

            # Wait
            try:
                response_message = await interaction.client.wait_for('message', check=check, timeout=60.0)  # 60 seconds timeout

                # MATCHES
                if response_message.content.strip().upper() == user_captcha_code:
                    if self.verification_role_id:
                        if role: 
                            await user.add_roles(role)
                            await user.send("You have been verified successfully!")
                            await interaction.followup.send(f"Yo! {user.mention}. You've been verified successfully.", ephemeral=True)
                    else:
                        await user.send("You have been verified successfully!")
                        await interaction.followup.send(f"Yo! {user.mention}. You've been verified successfully.", ephemeral=True)
                else:
                    await user.send("Incorrect CAPTCHA. Please try again by clicking the verify button again.")

            except asyncio.TimeoutError:
                await user.send("You took too long to respond. Please click the verify button again to try again.")
        #Set callback
        button.callback = on_button_click
        await channel.send(embed=embed, view=view)
        await interaction.response.send_message(f"Verification system set up in {channel.mention}.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(VerificationCog(bot))



# optional- if additional/alternative verification types can be added instead of captcha