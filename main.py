import discord
from discord.ext import commands
import youtube_dl
import os
import random

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

    elif str(message.channel) == "mod-mail" and message.content.startswith("<"):
        obj = message.mentions[0]
        if message.attachments != msgTable:
            files = message.attachments
            try:
                await obj.send("["+message.author.display_name+"]")
            except:
                pass

            for f in files:
                await obj.send(f.url)
        else:
            index = message.content.index(" ")
            text = message.content
            msg = text[index:]
            try:
                await obj.send("["+message.author.display_name+"] "+msg)
            except:
                pass

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
        kick [player] [reason]
        ban [player] [reason]
        unban [player]
        
        music:
        play
        resume
        pause
        stop
        leave
        
        game:
        tictactoe @[player1] @[player2]
        place [number]
        
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
async def kick(ctx, member : discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(member.mention + " kicked from server " + reason)

@client.command()
async def ban(ctx, member : discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(member.mention+" banned " + reason)

@client.command()
async def unban(ctx, *, member):
    bannedUsers = await ctx.guild.bans()
    name, discriminator = member.split('#')

    for b in bannedUsers:
        user = b.user
        if (name, discriminator) == (user.name, user.discriminator):
            await ctx.guild.unban(user)
            await ctx.send(member+" unbanned")
            return

#MUSIC
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

#TIC TAC TOE
winCondition = [
    [0,1,2],
    [3,4,5],
    [6,7,8],
    [0,3,6],
    [1,4,7],
    [2,5,8],
    [0,4,8],
    [2,4,6]
]

finished = True
turn = ""
player1 = ""
player2 = ""
board = []
score = 0

@client.command()
async def tictactoe(ctx, pl1 : discord.Member, pl2 : discord.Member):
    global finished
    global turn
    global player1
    global player2
    global score

    if finished:
        global board
        board = [
            ":white_large_square:", ":white_large_square:", ":white_large_square:",
            ":white_large_square:", ":white_large_square:", ":white_large_square:",
            ":white_large_square:", ":white_large_square:", ":white_large_square:"
        ]
        turn = ""
        finished = False;
        score = 0;
        player1 = pl1
        player2 = pl2

        board_line = ""
        for x in range(len(board)):         #print board
            if x==2 or x==5 or x==8:
                board_line += " " + board[x]
                await ctx.send(board_line)
                board_line = ""
            else:
                board_line += " " + board[x]

        StartNum = random.randint(1,2)
        if StartNum == 1:
            turn = player1
            await ctx.send("Player <@" + str(player1.id) + "> has turn")
        elif StartNum == 2:
            turn = player2
            await ctx.send("Player <@" + str(player2.id) + "> has turn")
        else:
            await ctx.send("Game already started...")

@client.command()
async def place(ctx, pos : int):
    global turn
    global player1
    global player2
    global board
    global score

    if not finished:
        flag = ""
        if turn == ctx.author:
            if turn == player1:
                flag=":regional_indicator_x:"
            elif turn == player2:
                flag=":o2:"

            if 0<pos<10 and board[pos-1] == ":white_large_square:":
                board[pos-1] = flag
                score+=1

                board_line = ""
                for x in range(len(board)):  # print board
                    if x == 2 or x == 5 or x == 8:
                        board_line += " " + board[x]
                        await ctx.send(board_line)
                        board_line = ""
                    else:
                        board_line += " " + board[x]

                checkGame(winCondition, flag)
                if finished:
                    await ctx.send(flag + " WINS!")
                elif score > 8:
                    await ctx.send("Its a tie!")

                #switch turn
                if turn == player1:
                    turn = player2
                elif turn == player2:
                    turn = player1

            else:
                await ctx.send("Please choose number between 1 and 9 and unmarked place")
        else:
            await ctx.send("It's not your turn")
    else:
        await ctx.send("Game is not running. Start it with !tictactoe command")

def checkGame(winCondition, flag):
    global finished
    for condition in winCondition:
        if board[condition[0]] == flag and board[condition[1]] == flag and board[condition[2]] == flag:
            finished = True

@tictactoe.error
async def tictactoeERROR(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please mention 2 players for this command")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("please mention/ping bot")

@place.error
async def place_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please enter correct position")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("please enter integer")

client.run('ODI5MzE2MTY2MDMwNzIxMDU1.YG2W3Q.Z8GYet4Qjb-EsvOcrkHN2q1e1-c')