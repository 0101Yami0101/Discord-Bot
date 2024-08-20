from better_profanity import profanity
import discord

if __name__ == "__main__":
    profanity.load_censor_words()

    text = "You p1ec3 of sHit."
    censored_text = profanity.censor(text)
    print(censored_text)
    # You **** of ****.

async def profanity_checker (message):
    if(profanity.contains_profanity(message.content)):
        await message.delete()
        embed= discord.Embed(
            title= "Warning!! ",
            description=f"Profanity Detected in a message sent by @{message.author.name}",
            color= discord.Color.red()
        )
        await message.channel.send(embed= embed)
    



