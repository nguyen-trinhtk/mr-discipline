import discord
from discord.ext import commands
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from datetime import date, datetime
from dotenv import load_dotenv
load_dotenv()

intents = discord.Intents.all()
PREFIX = '!'
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')

client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

commandList = ["!hello", "!help", "!play"]

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    content = message.content.lower()
    if content.startswith(bot.command_prefix) and content not in commandList:
        command_names = [command.name for command in bot.commands]
        recommendations = "\n".join(command_names)
        await message.channel.send(f"Did you mean one of these commands?\n{recommendations}")
    await bot.process_commands(message)

@bot.command()
async def hello(ctx):
    msg = "Hey there!"
    category = ""
    embed = discord.Embed(title=category, description=msg, color=discord.Color.green())
    await ctx.send(embed = embed)
bot.remove_command("help")

@bot.command()
async def help(ctx):
    msg = "!hello: Say hello to Mr.Discipline\n!help: List all available commands from Mr.Discipline\n!play `song name`: Play a song from Spotify"
    category = "Help"
    embed = discord.Embed(title=category, description=msg, color=discord.Color.green())
    await ctx.send(embed = embed)

@bot.command()
async def play(ctx, song_name):
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
            await ctx.send(embed = discord.Embed(title="", description="You are not in a voice channel.", color=discord.Color.green()))
            return

        voice_channel = ctx.author.voice.channel
        voice_client = await voice_channel.connect()

        embed = discord.Embed(title=category, description="", color=discord.Color.green())
        embed.set_thumbnail(url=track_image)
        embed.add_field(name="Listen on Spotify", value=f"[{track_name}]({track_url})")
        await ctx.send(embed=embed)

        voice_client.play(discord.FFmpegPCMAudio(track_uri))

        
    else:
        await ctx.send(embed = discord.Embed(title="", description="Song not found.", color=discord.Color.green()))
    
bot.run(os.getenv("TOKEN"))