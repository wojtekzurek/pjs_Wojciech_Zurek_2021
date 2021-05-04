import discord
from discord.ext import commands
import youtube_dl
import os

#client = discord.Client()
client = commands.Bot(command_prefix="!")

@client.event
async def on_message(message):
    message.content.lower()
    msgTable = []   #empty table
    modMailChannel = discord.utils.get(client.get_all_channels(), name="mod-mail")

    if message.author == client.user:
        return
    elif message.content.startswith("hello"):       #welcome message
        await message.channel.send("Hello " + str(message.author) + ", my name is Cogwheel")
    elif message.content.startswith("hi"):
        await message.channel.send("hi " + str(message.author) + ", welcome to server")
    elif str(message.channel) == "ogólny" and "fuck" in message.content:       #delete message
        await message.channel.purge(limit=1)
    elif str(message.channel.type) == "private":        #advanced mod-mail
        #modMailChannel = discord.utils.get(client.get_all_channels(), name="mod-mail")      #private message
        if message.attachments != msgTable:
            files = message.attachments
            await modMailChannel.send("["+message.author.display_name+"] ")

            for f in files:
                await modMailChannel.send(f.url)
        else:
            await modMailChannel.send("["+message.author.display_name+"] "+message.content)

    elif str(message.channel) == "mod-mail" and message.content.startswith("<"):    #ERROR
        obj = message.mentions[0]
        if message.attachments != msgTable:
            files = message.attachments
            await obj.send("["+message.author.display_name+"]")     #ERROR

            for f in files:
                await obj.send(f.url)
        else:
            index = message.content.index(" ")
            text = message.content
            msg = text[index:]
            await obj.send("["+message.author.display_name+"] "+msg)

    await client.process_commands(message)      #for client.commands

@client.command()
async def say(ctx, *msg):
    for element in msg:
        await ctx.send(element)

@client.command()
async def list(ctx):
    info="""COGWHEEL BOT INFORMATION
        command prefix = '!'
        
        say [arg]\t\t-print arg
        server\t\t\t -check information about server
        list\t\t\t\t   -print commands list
        """
    await ctx.send(info)

@client.command()
async def server(ctx):
    name = str(ctx.guild.name)
    desc = str(ctx.guild.description)
    owner = str(ctx.guild.owner)
    id = str(ctx.guild.id)
    region = str(ctx.guild.region)
    memberCount = str(ctx.guild.member_count)
    icon = str(ctx.guild.icon_url)

    embed = discord.Embed(
        title=name+" information",
        description=desc,
        color=discord.Color.dark_blue()
    )
    embed.set_thumbnail(url=icon)
    embed.add_field(name="Owner", value=owner, inline=True)
    embed.add_field(name="Server ID", value=id, inline=True)
    embed.add_field(name="Region", value=region, inline=True)
    embed.add_field(name="Member Count", value=memberCount, inline=True)

    await ctx.send(embed=embed)

@client.command()
async def play(ctx, url : str):
    music = os.path.isfile("song.mp3")
    try:
        if music:
            os.remove("song.mp3")
    except PermissionError:
        await ctx.send("Please wait for currently song end or use stop command")

    voiceChannel = discord.utils.get(ctx.guild.voice_channels, name="Ogólne")
#    if not voiceChannel.is_connected():
    await voiceChannel.connect()
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

#    if not voice.is_connected():
#        await voiceChannel.connect()

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    for f in os.listdir("./"):
        if f.endswith(".mp3"):
            os.rename(f, "song.mp3")

    voice.play(discord.FFmpegPCMAudio("song.mp3"))

@client.command()
async def leave(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

    if voice.is_connected():
        await voice.disconnect();
    else:
        await ctx.send("I'm not connected to any voice channel")

@client.command()
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

    if voice.is_playing():
        voice.pause();
    else:
        ctx.send("Audio paused a some time ago...")

@client.command()
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

    if voice.is_paused():
        voice.resume()
    else:
        ctx.send("Audio is not pasued...")

@client.command()
async def stop(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    voice.stop()
    await voice.disconnect()


client.run('ODI5MzE2MTY2MDMwNzIxMDU1.YG2W3Q.Z8GYet4Qjb-EsvOcrkHN2q1e1-c')