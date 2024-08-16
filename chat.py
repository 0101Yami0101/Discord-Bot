import os
from discord.ext import commands
import cohere

cohere_api_key = os.getenv("COHERE_KEY")
co = cohere.Client(cohere_api_key)

@commands.command(name="ai")
async def chatbot(ctx, *, message: str):
    try:
        
        response = co.generate(
            model='command-xlarge-nightly',  
            prompt=message,
            max_tokens=100, 
            temperature=0.7
        )
        response_text = response.generations[0].text.strip()

        await ctx.send(response_text)
    
    except Exception as e:

        await ctx.send(f"An error occurred: {e}")

