# bot.py
import os
import random
import discord
import threading
import asyncio
from dotenv import load_dotenv
from time import sleep
from random import randint
from discord.ext import commands

load_dotenv()

client = discord.Client()
bot = commands.Bot(command_prefix='$')
base_sound_dir = os.getenv('BASE_SOUND_DIR')
base_ffmpeg_dir = os.getenv('BASE_FFMPEG_DIR')
TOKEN = os.getenv('DISCORD_TOKEN')
task = None

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.command(name="play")
async def sons(ctx, arg):
    await ctx.message.delete()
    client.loop.create_task(play_audio(ctx, arg))

@bot.command(name="sounds")
async def som(ctx):
    await ctx.message.delete()
    files = os.listdir(f"{base_sound_dir}/random-sounds")
    lista = '\nSons disponíveis: \n'
    for f in files:
        if f.endswith(".mp3"):
            lista = lista + f"{f}\n"

    print(lista)
    await ctx.send(str(lista))
    
@bot.command(name="start-wezoa-talk")
async def conversa_wezoa(ctx):
    await ctx.message.delete()
    client.loop.create_task(loop_sounds(ctx, "wezoa"), name="wezoa_talk")

@bot.command(name="start-random-talk")
async def conversa_random(ctx):
    await ctx.message.delete()
    client.loop.create_task(loop_sounds(ctx, "random"), name="random_talk")

@bot.command(name="leave")
async def sair(ctx):
    await ctx.message.delete()
    task = [task for task in asyncio.all_tasks() if task != None and task.get_name() == "wezoa_talk" or task.get_name() == "random_talk"]
    if len(task) > 0:
        task[0].cancel()
    print('saindo')
    voice_client = ctx.message.guild.voice_client
    await voice_client.disconnect()

async def loop_sounds(ctx, folder):
    # Gets voice channel of message author
    author_voice_channel = ctx.author.voice.channel
    bot_voice_channel = None

    if ctx.voice_client:
        bot_voice_channel = ctx.voice_client.channel

    if author_voice_channel != None:
        current_voice_channel = None

        if author_voice_channel != bot_voice_channel:
            current_voice_channel = await author_voice_channel.connect()
        else:
            current_voice_channel = ctx.bot.voice_clients[0]

        while True:
            audio = random.choice(os.listdir(f"{base_sound_dir}/{folder}-sounds"))

            current_voice_channel.play(discord.FFmpegPCMAudio(
                # trocar para wezoa-sounds depois
                executable=f"{base_ffmpeg_dir}/ffmpeg.exe", source=f"{base_sound_dir}/{folder}-sounds/{audio}"))

            print(f'{ctx.author.name} está o tocando som {audio}')
            # Sleep while audio is playing.
            while current_voice_channel.is_playing():
                await asyncio.sleep(3)
                
            await asyncio.sleep(randint(5, 30))
    else:
        await ctx.send(str(ctx.author.name) + "is not in a channel.")

async def play_audio(ctx, arg):
    if os.path.exists(f'{base_sound_dir}/random-sounds/{arg}.mp3'):
        # Gets voice channel of message author
        author_voice_channel = ctx.author.voice.channel
        bot_voice_channel = None
        
        if ctx.voice_client:
            bot_voice_channel = ctx.voice_client.channel

        if author_voice_channel != None:
            current_voice_channel = None
            if author_voice_channel != bot_voice_channel:
                current_voice_channel = await author_voice_channel.connect()
            else:
                current_voice_channel = ctx.bot.voice_clients[0]

            while current_voice_channel.is_playing():
                await asyncio.sleep(3)

            current_voice_channel.play(discord.FFmpegPCMAudio(
                executable=f"{base_ffmpeg_dir}/ffmpeg.exe", source=f"{base_sound_dir}/random-sounds/{arg}.mp3"))

            print(f'{ctx.author.name} está o tocando som {arg}.mp3')
            # Sleep while audio is playing.
            while current_voice_channel.is_playing():
                await asyncio.sleep(3)
        else:
            await ctx.send(str(ctx.author.name) + "is not in a channel.")        
    else:
        await ctx.send(f'{arg}.mp3 não encontrado')
        print(f'{arg}.mp3 não encontrado')  


bot.run(TOKEN)
client.run(TOKEN)