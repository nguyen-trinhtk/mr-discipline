import discord
from discord.ext import commands
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import random
from dotenv import load_dotenv
import json
import time
import datetime
from datetime import datetime
import asyncio 
load_dotenv()
#bot
intents = discord.Intents.all()
intents.message_content = True
intents.voice_states = True
#prefix
default_prefix = '!'
#greetings
greets = ['Hi', 'Hello', 'Welcome back', 'Greetings', 'Long time no see', 'Aww I miss you sooo mwch']
#spotify
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
#quiz
boo = ["Unculture!", "Try again!", "Booo!", "???"]
#json functions
def load_guild_setup(filepath: str):
    try:
        with open(filepath, "r") as file:
            guild_setup = json.load(file)
    except FileNotFoundError:
        guild_setup = {}
    return guild_setup

def save_guild_setup(guild_setup, filepath:str):
    with open(filepath, "w") as file:
        json.dump(guild_setup, file)
#text function
def embedText(msg, title=None):
    if not title:
        return discord.Embed(title="", description=msg, color=discord.Color.green())
    return discord.Embed(title=title, description=msg, color=discord.Color.green())

guild_prefixes = load_guild_setup("prefixes.json")
guild_notes = load_guild_setup("notes.json")
guild_boolean = load_guild_setup("boolean.json")
def get_prefix(bot, message):
    if message:
        if str(message.guild.id) in guild_prefixes:
            return guild_prefixes[str(message.guild.id)]
    return '!'
#cmd bot
bot = commands.Bot(command_prefix=get_prefix, intents=intents)
#events
@bot.event
async def on_ready():
        print("Mr.Discipline is in {} guild(s)".format(len(bot.guilds)))
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)

@bot.event
async def on_disconnect():
    save_guild_setup(guild_prefixes, "prefixes.json")

@bot.command()
async def ping(ctx):
        await ctx.send(f"pong")

@bot.command()
async def setprefix(ctx, new_prefix: str):
        guild_prefixes.update({str(ctx.message.guild.id):new_prefix})
        save_guild_setup(guild_prefixes, "prefixes.json")
        await ctx.send(embed=embedText("Prefix changed to "+ new_prefix))
        print(guild_prefixes)
@bot.command()
async def getprefix(ctx):
    guild_id = str(ctx.guild.id)
    if guild_id in guild_prefixes:
        msg = "Server's current prefix is "+ guild_prefixes[guild_id]
        await ctx.send(embed=embedText(msg)) 
    else: 
        await ctx.send(embed=embedText('The default prefix for this server is !'))
    
    
@bot.command()
async def hello(ctx):
    msg = "{}, {}!".format(random.choice(greets), ctx.message.author)
    await ctx.send(embed = embedText(msg))

bot.remove_command("help")

@bot.command()
async def help(ctx):
    msg = "hello: Say hello to Mr.Discipline\nhelp: List all available commands from Mr.Discipline\nplay `song name`: Play a song from Spotify"
    await ctx.send(embed = embedText(msg, "Help"))

#spotify
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
    
#quiz
@bot.command()
async def quizset(ctx, *quizname):
    guild_id = str(ctx.message.guild.id)
    quizname = " ".join(quizname)
    if not quizname:
        quizname = ""
    await ctx.send(embed=embedText("Example: \n`cat: a sharp-eared animal`, `dog: my favorite animal`", "Insert a list of more than one word-colon-meaning's, seperate by commas"))
    while True:
        msg = await bot.wait_for("message", timeout=60)
        quizContent = '{"' + msg.content + '"}'
        quizContent = quizContent.replace(' , ', ',').replace(', ', ',').replace(' ,', ',').replace(' : ', ':').replace(': ', ':').replace(' :', ':').replace(':', '":"').replace(',', '","')
        if not ':' in msg.content or not ',' in msg.content:
            await ctx.send(embed=embedText("Please type in the right format.", quizname.capitalize()))
        else: 
            await ctx.send(embed=embedText('Got it!', quizname.capitalize()))
            filename = 'quiz'+ quizname.replace(' ', '_') +".json"
            with open("mr-discipline/jsons/"+filename, "w") as f:
                f.write(quizContent)
            break
    #edit quizset

@bot.command()
async def quizplay(ctx):
    pass

@bot.command()
async def quizstop(ctx):
    global quizzing
    quizzing = False

@bot.command()
async def quizremove(ctx):
    pass

@bot.command()
async def quizappend(ctx):
    pass

#timer
@bot.command()
async def timer(ctx, sec: int, min: int, hour: int):
    sleep_duration = sec + min * 60 + hour * 3600
    remaining_time = datetime.timedelta(seconds=sleep_duration)
    message = await ctx.send(f"Timer: {remaining_time} remaining")

    while sleep_duration > 0:
        await asyncio.sleep(0.63)
        sleep_duration -= 1
        remaining_time = datetime.timedelta(seconds=sleep_duration)
        await message.edit(content=f"Timer: {remaining_time} remaining")

@timer.error
async def focus_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(embed=embedText("Please provide the duration in seconds, minutes and hour"))

@bot.command()
async def stopwatch(ctx):
    hours = 0
    minutes = 0
    seconds = 0
    msg = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    stopwatch_message = await ctx.send(embed=embedText(msg))
    while True:
        await asyncio.sleep(0.63)
        seconds += 1
        if seconds >= 60:
            seconds = 0
            minutes += 1
        if minutes >= 60:
            minutes = 0
            hours += 1
        msg = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        await stopwatch_message.edit(embed=embedText(msg))

@stopwatch.error
async def stopwatch_error(ctx, error):
    await ctx.send("An error occurred while running the stopwatch command.")


@bot.command()
async def alarm(ctx, time: str):


@bot.command()
async def focus(ctx, min: int, hour: int):
    sleep_duration = min * 60 + hour * 3600
    remaining_time = datetime.timedelta(seconds=sleep_duration)
    message = await ctx.send(f"Focus session: {remaining_time} remaining")

    while sleep_duration > 0:
        await asyncio.sleep(0.63)
        sleep_duration -= 1
        remaining_time = datetime.timedelta(seconds=sleep_duration)
        await message.edit(content=f"Focus session: {remaining_time} remaining")

    await ctx.send("You are in a focus session")

@focus.error
async def focus_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please provide the duration in minutes and hour")

@bot.command()
async def donefocus(ctx):
    global focus 
    focus = False
#note
@bot.command
async def newnote(ctx, *notename):
    guild_id = str(ctx.message.guild.id)
    notename = " ".join(notename)
    if not notename:
        notename  = ""
    await ctx.send(embed=embedText("Please insert your note."))
    msg = await bot.wait_for("message", timeout=60)
    noteContent = msg.content
    guild_notes[guild_id][notename] = noteContent
    save_guild_setup(guild_notes, "notes.json")
    await ctx.send(embed=embedText("Note successfully added!"))

@bot.command
async def removenote(ctx, *notename):
    guild_id = str(ctx.message.guild.id)
    notename = " ".join(notename)
    if not notename:
        notename  = ""
    if notename in guild_notes[guild_id]:
        guild_notes[guild_id].pop(notename)
        save_guild_setup(guild_notes, "notes.json")
        await ctx.send(embed=embedText("Note successfully removed!"))
    else:
        await ctx.send(embed=embedText('Note not found.'))


@bot.command 
async def viewnote(ctx, *notename):
    guild_id = str(ctx.message.guild.id)
    notename = " ".join(notename)
    guild_dict = guild_notes[guild_id]
    if not notename in guild_dict:
        await ctx.send(embed=embedText("Note not found."))
    else:
        noteContent = guild_dict[notename]
        await ctx.send(embed=embedText(noteContent, notename))

@bot.command
async def showallnotes(ctx):
    guild_id = str(ctx.message.guild.id)
    guild_dict = guild_notes[guild_id]
    msg = ""
    cnt = 0
    for name, content in guild_dict:
        msg += str(cnt) + " - " + name + "\n"
        cnt += 1
    await ctx.send(embed=embedText(msg, "Here are your notes: "))


#riemann
@bot.command()
async def aespa(ctx):
    with open("mr-discipline/jsons/aespa.json", "r") as asap:
        questions = json.load(asap)
    for key, value in questions.items():
        await ctx.send(embed=embedText(key))
        message = await bot.wait_for("message", timeout=60)
        user_answer = message.content.lower().strip()
        if not user_answer:
            await ctx.send("Timeout!")
            return
        if user_answer == value:
            pass
        else:
            await ctx.send(embed=embedText(random.choice(boo)))
            return
    await ctx.send(embed=embedText("Congrats! You answered all the questions correctly."))

@bot.command()
async def stop(ctx):
    pass

bot.run(os.getenv("TOKEN"), root_logger=True)
