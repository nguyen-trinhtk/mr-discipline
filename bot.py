import discord
import os
from dotenv import load_dotenv
import random

#initializing responses
greetings = ['Hello there!', 'Hi', "I'm here", "You called me?", "Present!"]

def handle_response(message) -> str:
    msg = message.lower()

    if msg == 'hello':
        return random.choice(greetings)
    
    if msg == 'roll':
        return str(random.randint(1,6))

load_dotenv('token.env')

async def send_message(message, user_message, is_private):
    try: 
        response = handle_response(user_message)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e: 
        print(e)

    
def run_discord_bot():
    load_dotenv('token.env')
    intents = discord.Intents.default()
    bot = discord.Client(intents=intents)

    @bot.event
    async def on_ready():
        guildCnt = 0

        for guild in bot.guilds:
            print(f"- {guild.id} (name: {guild.name})")
            guildCnt += 1

        print("Mr.Discipline is in {} guild(s)".format(guildCnt))

    bot.run(os.getenv('TOKEN'))

run_discord_bot()