import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import datetime
import requests
from bs4 import BeautifulSoup
import json

load_dotenv()

client = commands.Bot(command_prefix='!', intents=discord.Intents.default())

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.command(name='hello')
async def hello(ctx):
    await ctx.send(f'Hello {ctx.author.name}!')

@client.command(name='ping')
async def ping(ctx):
    latency = round(client.latency * 1000)
    await ctx.send(f'Pong! {latency}ms')

@client.command(name='time')
async def get_time(ctx):
    current_time = datetime.datetime.now()
    await ctx.send(f'Current time: {current_time}')

@client.command(name='quote')
async def get_quote(ctx):
    response = requests.get('https://api.quotable.io/random')
    if response.status_code == 200:
        data = response.json()
        quote = data['content']
        author = data['author']
        await ctx.send(f'"{quote}" - {author}')
    else:
        await ctx.send('Could not fetch quote at this time.')

@client.command(name='weather')
async def get_weather(ctx, city: str):
    api_key = os.getenv('WEATHER_API_KEY')
    if not api_key:
        await ctx.send('Weather API key not configured.')
        return
    
    url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        temp = data['main']['temp']
        description = data['weather'][0]['description']
        await ctx.send(f'Weather in {city}: {temp}°C, {description}')
    else:
        # 用户未接受协议：显示协议内容
        send_message(
            chat_id,
            "Before joining the Support Group, confirm:\n\n"
            "✅ I will not DM members for 'help'\n"
            "✅ I will never share OTP / PIN / passwords\n"
            "✅ I will follow only official posts from this bot/channel\n\n"
            "Press I Agree to continue.",
            reply_markup=pledge_keyboard(),
        )
        await ctx.send(f'Could not fetch weather for {city}.')

@client.command(name='user_info')
async def user_info(ctx, user: discord.User):
    embed = discord.Embed(title=f'User Info: {user.name}', color=discord.Color.blue())
    embed.add_field(name='User ID', value=user.id, inline=False)
    embed.add_field(name='Account Created', value=user.created_at, inline=False)
    embed.add_field(name='Bot', value=user.is_bot, inline=False)
    await ctx.send(embed=embed)

@client.command(name='help_custom')
async def help_custom(ctx):
    embed = discord.Embed(title='Bot Commands', color=discord.Color.green())
    embed.add_field(name='!hello', value='Greet the user', inline=False)
    embed.add_field(name='!ping', value='Check bot latency', inline=False)
    embed.add_field(name='!time', value='Get current time', inline=False)
    embed.add_field(name='!quote', value='Get a random quote', inline=False)
    embed.add_field(name='!weather [city]', value='Get weather for a city', inline=False)
    embed.add_field(name='!user_info [user]', value='Get information about a user', inline=False)
    await ctx.send(embed=embed)

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content.startswith('hello'):
        await message.channel.send(f'Hello {message.author.name}!')
    
    await client.process_commands(message)

token = os.getenv('DISCORD_TOKEN')
client.run(token)
