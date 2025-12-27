# Discord Bot - DhanWorks

A Discord bot with various useful commands including weather, quotes, user info, and more.

## Features

- 👋 Greetings and ping commands
- 🌤️ Weather information
- 💬 Random quotes
- ⏰ Current time
- 👤 User information
- 📋 Custom help command

## Commands

- `!hello` - Greet the user
- `!ping` - Check bot latency
- `!time` - Get current time
- `!quote` - Get a random quote
- `!weather [city]` - Get weather for a city
- `!user_info [user]` - Get information about a user
- `!help_custom` - Display all available commands

## Setup on Ubuntu Server

### Quick Setup

1. **Clone/upload the repository to your server**
```bash
cd /home/botuser
# Upload your files here
```

2. **Run the deployment script**
```bash
chmod +x deploy.sh run.sh setup_service.sh
./deploy.sh
```

3. **Configure your environment variables**
```bash
nano .env
```

Add your tokens:
- `DISCORD_TOKEN` - Get from [Discord Developer Portal](https://discord.com/developers/applications)
- `WEATHER_API_KEY` - Get from [OpenWeatherMap](https://openweathermap.org/api)

4. **Test the bot**
```bash
./run.sh
```

### Running as a Service (Auto-start on boot)

To run the bot as a background service that starts automatically:

```bash
sudo ./setup_service.sh
```

**Service Management Commands:**
```bash
# Check status
sudo systemctl status discord-bot

# View logs
sudo journalctl -u discord-bot -f

# Restart bot
sudo systemctl restart discord-bot

# Stop bot
sudo systemctl stop discord-bot
```

## Manual Installation

If you prefer to install manually:

```bash
# Install Python and dependencies
sudo apt update
sudo apt install -y python3 python3-pip python3-venv

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install packages
pip install -r requirements.txt

# Create .env file
cp .env.example .env
nano .env  # Add your tokens

# Run the bot
python3 bot.py
```

## Getting Discord Bot Token

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application"
3. Give it a name and create
4. Go to "Bot" section in the left sidebar
5. Click "Add Bot"
6. Under "Token" section, click "Copy" to get your token
7. Enable required intents (Message Content Intent, Server Members Intent)
8. Go to "OAuth2" → "URL Generator"
9. Select scopes: `bot`
10. Select permissions: Based on your needs
11. Copy the generated URL and open it to invite the bot to your server

## Troubleshooting

### Bot not responding
- Check if the bot is online in Discord
- Verify the token in `.env` is correct
- Check logs: `sudo journalctl -u discord-bot -f`

### Module not found errors
- Activate virtual environment: `source venv/bin/activate`
- Reinstall requirements: `pip install -r requirements.txt`

### Permission errors
- Make sure scripts are executable: `chmod +x *.sh`
- Check service file ownership and permissions

## Support

For issues and questions, please open an issue in the repository.

