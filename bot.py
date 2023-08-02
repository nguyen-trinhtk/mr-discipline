import discord
from discord.ext import commands
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import random
from dotenv import load_dotenv
import json
load_dotenv()

intents = discord.Intents.all()
intents.message_content = True
intents.voice_states = True
PREFIX = '!'
bot = commands.Bot(command_prefix=PREFIX, intents=intents)


CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')

client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
commandList = [PREFIX+"hello",PREFIX+"help",PREFIX+"play",PREFIX+"quizset",PREFIX+"aespa"]
boo = ["Unculture! Again!", "Try again!", "Booo! Again", "???? Again"]


def embedText(msg, title=None):
    if not title:
        return discord.Embed(title="", description=msg, color=discord.Color.green())
    return discord.Embed(title=title, description=msg, color=discord.Color.green())

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    content = message.content.lower()
    if content.startswith(bot.command_prefix) and (content.split()[0].strip()) not in commandList:
        print(bot.commands)
        print(content.split()[0].strip())
        command_names = [command.name for command in bot.commands]
        recommendations = "\n".join(command_names)
        embed = embedText(recommendations, "Did you mean one of these commands?")
        await message.channel.send(embed=embed)
    await bot.process_commands(message)
    return message.content

@bot.command()
async def hello(ctx):
    await ctx.send(embed = embedText("Hey there!"))

bot.remove_command("help")

@bot.command()
async def help(ctx):
    msg = "!hello: Say hello to Mr.Discipline\n!help: List all available commands from Mr.Discipline\n!play `song name`: Play a song from Spotify"
    await ctx.send(embed = embedText(msg, "Help"))

@bot.command()
async def play(ctx, *song_name):
    if song_name==None:
        await ctx.send(embedText("Enter a valid song name"))
        return
    else:
        song_name = " ".join(song_name)
        results = spotify.search(q='track:' + song_name, type='track', limit=1)
        if results['tracks']['items']:
            track = results['tracks']['items'][0]
            track_name = track['name']
            track_artist = track['artists'][0]['name']
            track_url = track['external_urls']['spotify']
            track_image = track['album']['images'][0]['url']
            track_uri = track['uri']
            category = "Now playing: "+ track_name + " by " + track_artist

            if ctx.author.voice is None or ctx.author.voice.channel is None:
                await ctx.send(embed=embedText("You are not in a voice channel"))
                return

            voice_channel = ctx.author.voice.channel
            voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
            if voice_client and voice_client.is_connected():
                await voice_client.move_to(voice_channel)
            else:
                voice_client = await voice_channel.connect()

            embed = embedText("", category)
            embed.set_thumbnail(url=track_image)
            embed.add_field(name="Listen on Spotify", value=f"[{track_name}]({track_url})")
            await ctx.send(embed=embed)

            voice_client.play(discord.FFmpegPCMAudio(track_uri), after=await ctx.send(embed=embedText("End of song.")))

        else:
            await ctx.send(embed=embedText("Song not found, please try another."))
    

@bot.command()
async def quizset(ctx, *quizname):
    quizname = " ".join(quizname)
    if not quizname:
        quizname = ""
    await ctx.send(embed=embedText("Example: \n`cat: a sharp-eared animal`, `dog: my favorite animal`", "Insert a list of more than one word-colon-meaning's, seperate by commas"))
    while True:
        msg = await bot.wait_for("message", timeout=60)
        if not ':' in msg or not ',' in msg:
            await ctx.send(embed=embedText("Please type in the right format.", quizname.capitalize()))
        else: 
            await ctx.send(embed=embedText('Got it!', quizname.capitalize()))
            return msg

@bot.command()
async def asap(ctx):
    questions = {'K': 'rkpc', 'W': 'rkpc', 'G': 'rkpc', 'N': 'rkpc'}
    for i in range(len(questions)):
        current = questions[i]
        await ctx.send(embed=embedText(current))
        message = await bot.wait_for("message", timeout=60)
        user_answer = message.content.lower().strip()
        if not user_answer:
            await ctx.send("Timeout!")
            return
        if user_answer == questions[current]:
            pass
        else:
            await ctx.send(embed=embedText(random.choice(boo)))
            return
    await ctx.send(embed=embedText("Congrats! You answered all the questions correctly."))
        
bot.run(os.getenv("TOKEN"))