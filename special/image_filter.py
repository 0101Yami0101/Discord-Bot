import requests
from nudenet import NudeDetector
import os
from discord.ext import commands
from Moderation.auto_mod_init import  userViolationCount
from Moderation import auto_mod_init

detector = NudeDetector()


class ImageFilterCog(commands.Cog):
    def __init__(self, bot):
        self.bot= bot
        self.image_directory = "data/images/"
        os.makedirs(self.image_directory, exist_ok=True)

    
    def is_nsfw(self, detection_results, threshold=0.5):

        nsfw_classes = {
            'MALE_GENITALIA_EXPOSED',
            'FEMALE_BREAST_EXPOSED',
            'FEMALE_GENITALIA_EXPOSED',
            'BUTTOCKS_EXPOSED'
        }


        for detection in detection_results:
            detected_class = detection['class']
            score = detection['score']
            if detected_class in nsfw_classes and score >= threshold:
                return True 

        return False 


    @commands.Cog.listener()
    async def on_message(self, message):
        
        if "imagefilter" not in auto_mod_init.moderationSession:
            return

        if message.author == self.bot.user:
            return
        if message.attachments:
            for attachment in message.attachments:
                if attachment.content_type and 'image' in attachment.content_type:
                    image_path = os.path.join(self.image_directory, attachment.filename)
                    await attachment.save(image_path)

                    if image_path:
                        try:
                            detector = NudeDetector()
                            result = detector.detect(image_path)
                            if self.is_nsfw(result):
                                await message.delete()
                                
                                # Increment violation count
                                user_id = message.author.id
                                if user_id in userViolationCount:
                                    userViolationCount[user_id] += 1
                                else:
                                    userViolationCount[user_id] = 1
                                    
                                # Send a warning message
                                await message.channel.send(f"⚠️ {message.author.mention}. Image contains NSFW content. Please avoid uploading NSFW images.")

                        finally:
                            if os.path.exists(image_path):
                                os.remove(image_path)

                                

    
        
async def setup(bot: commands.Bot):
    await bot.add_cog(ImageFilterCog(bot))


