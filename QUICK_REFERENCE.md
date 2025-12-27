# dhanworks-bot Quick Reference Guide

**Last Updated:** 2025-12-27  
**Version:** 1.0

---

## Table of Contents

1. [Database Operations](#database-operations)
2. [User Operations](#user-operations)
3. [Bot Integration](#bot-integration)
4. [Common Commands](#common-commands)
5. [Troubleshooting](#troubleshooting)
6. [API Endpoints](#api-endpoints)

---

## Database Operations

### Connection Setup

```python
from dhanworks_bot.database import DatabaseConnection

# Initialize database connection
db = DatabaseConnection(
    host='localhost',
    port=5432,
    database='dhanworks_bot',
    user='bot_user',
    password='your_password'
)

# Connect to database
db.connect()
```

### Common Database Tasks

#### Create a New Record

```python
# Insert user data
db.insert('users', {
    'username': 'john_doe',
    'email': 'john@example.com',
    'created_at': datetime.now(),
    'status': 'active'
})
```

#### Query Data

```python
# Select all active users
users = db.query('SELECT * FROM users WHERE status = %s', ('active',))

# Select with parameters
user = db.query_one('SELECT * FROM users WHERE username = %s', ('john_doe',))
```

#### Update Records

```python
# Update user status
db.update('users', {'status': 'inactive'}, {'username': 'john_doe'})
```

#### Delete Records

```python
# Delete inactive users
db.delete('users', {'status': 'inactive'})
```

### Transaction Management

```python
# Begin transaction
db.begin_transaction()

try:
    db.insert('users', user_data)
    db.update('logs', log_data)
    db.commit()  # Commit changes
except Exception as e:
    db.rollback()  # Rollback on error
    raise e
```

### Database Backup & Maintenance

```bash
# Backup database
pg_dump dhanworks_bot > backup_$(date +%Y%m%d).sql

# Restore from backup
psql dhanworks_bot < backup_20251227.sql

# Optimize database
VACUUM ANALYZE;
```

---

## User Operations

### User Management

#### Create New User

```python
from dhanworks_bot.user import UserManager

user_manager = UserManager(db)

# Create user
new_user = user_manager.create_user(
    username='alice_smith',
    email='alice@example.com',
    role='member',
    metadata={'timezone': 'UTC'}
)
```

#### Retrieve User Information

```python
# Get user by ID
user = user_manager.get_user(user_id=123)

# Get user by username
user = user_manager.get_user_by_username('alice_smith')

# Get all users with filters
users = user_manager.list_users(
    role='admin',
    status='active',
    limit=50,
    offset=0
)
```

#### Update User Profile

```python
# Update user information
user_manager.update_user(
    user_id=123,
    updates={
        'email': 'newemail@example.com',
        'timezone': 'EST',
        'preferences': {'notifications': True}
    }
)
```

#### Delete User

```python
# Soft delete (deactivate)
user_manager.deactivate_user(user_id=123)

# Hard delete (permanent)
user_manager.delete_user(user_id=123, permanent=True)
```

### User Roles & Permissions

```python
# Assign role to user
user_manager.assign_role(user_id=123, role='moderator')

# Grant specific permission
user_manager.grant_permission(user_id=123, permission='edit_posts')

# Revoke permission
user_manager.revoke_permission(user_id=123, permission='edit_posts')

# Check user permissions
has_permission = user_manager.has_permission(user_id=123, permission='delete_posts')
```

### User Sessions & Authentication

```python
# Create session
session_token = user_manager.create_session(user_id=123, duration=3600)

# Validate session
is_valid = user_manager.validate_session(session_token)

# Logout user
user_manager.logout(session_token)

# Get active sessions
sessions = user_manager.get_active_sessions(user_id=123)
```

---

## Bot Integration

### Bot Initialization

```python
from dhanworks_bot import DhanworksBot
from dhanworks_bot.config import Config

# Load configuration
config = Config(env='production')

# Initialize bot
bot = DhanworksBot(
    token=config.BOT_TOKEN,
    intents=config.INTENTS,
    command_prefix='!',
    database=db
)
```

### Event Handlers

#### Message Events

```python
@bot.event
async def on_message(message):
    """Handle incoming messages"""
    if message.author == bot.user:
        return
    
    await bot.process_commands(message)

@bot.event
async def on_message_edit(before, after):
    """Handle edited messages"""
    print(f"Message edited: {before.content} → {after.content}")
```

#### Member Events

```python
@bot.event
async def on_member_join(member):
    """Welcome new members"""
    channel = bot.get_channel(config.WELCOME_CHANNEL_ID)
    await channel.send(f"Welcome {member.mention}!")

@bot.event
async def on_member_remove(member):
    """Handle member leaving"""
    log_channel = bot.get_channel(config.LOG_CHANNEL_ID)
    await log_channel.send(f"{member.name} has left the server")
```

### Commands

#### Basic Commands

```python
from discord.ext import commands

@bot.command(name='ping')
async def ping(ctx):
    """Check bot latency"""
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')

@bot.command(name='userinfo')
async def userinfo(ctx, member: discord.Member = None):
    """Get user information"""
    member = member or ctx.author
    embed = discord.Embed(title=f"User Info: {member}")
    embed.add_field(name="ID", value=member.id)
    embed.add_field(name="Joined", value=member.joined_at)
    await ctx.send(embed=embed)
```

#### Command Groups

```python
@bot.group(name='user')
async def user_group(ctx):
    """User management commands"""
    if ctx.invoked_subcommand is None:
        await ctx.send("Please specify a subcommand")

@user_group.command(name='create')
async def create_user(ctx, username: str):
    """Create new user"""
    user = user_manager.create_user(username=username)
    await ctx.send(f"User created: {user['username']}")

@user_group.command(name='delete')
async def delete_user(ctx, user_id: int):
    """Delete user"""
    user_manager.delete_user(user_id)
    await ctx.send(f"User {user_id} deleted")
```

#### Commands with Permissions

```python
@bot.command(name='kick')
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    """Kick a member"""
    await member.kick(reason=reason)
    await ctx.send(f"{member.mention} has been kicked")

@kick.error
async def kick_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to use this command")
```

### Sending Messages

#### Text Messages

```python
# Simple message
await ctx.send("Hello, world!")

# Message with mentions
await ctx.send(f"Hello {ctx.author.mention}!")

# Message with file
await ctx.send(file=discord.File('path/to/file.txt'))
```

#### Embeds

```python
embed = discord.Embed(
    title="Title",
    description="Description text",
    color=discord.Color.blue()
)
embed.add_field(name="Field 1", value="Value 1", inline=False)
embed.add_field(name="Field 2", value="Value 2", inline=True)
embed.set_image(url="https://example.com/image.png")
embed.set_footer(text="Footer text")

await ctx.send(embed=embed)
```

### Scheduled Tasks

```python
from discord.ext import tasks

@tasks.loop(hours=1)
async def hourly_task():
    """Runs every hour"""
    print("Hourly task executing")

@hourly_task.before_loop
async def before_hourly_task():
    await bot.wait_until_ready()

hourly_task.start()
```

### Error Handling

```python
@bot.event
async def on_command_error(ctx, error):
    """Global error handler"""
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Missing required argument: {error.param.name}")
    else:
        await ctx.send(f"Error: {str(error)}")
```

---

## Common Commands

### User Management

| Command | Description | Usage |
|---------|-------------|-------|
| `!user create` | Create new user | `!user create username` |
| `!user delete` | Delete user | `!user delete user_id` |
| `!userinfo` | Get user info | `!userinfo @mention` |
| `!user role` | Assign role | `!user role user_id role_name` |
| `!user list` | List users | `!user list --role admin` |

### Moderation

| Command | Description | Usage |
|---------|-------------|-------|
| `!kick` | Kick member | `!kick @member reason` |
| `!ban` | Ban member | `!ban @member reason` |
| `!warn` | Warn member | `!warn @member reason` |
| `!mute` | Mute member | `!mute @member duration` |
| `!purge` | Delete messages | `!purge 10` |

### Utility

| Command | Description | Usage |
|---------|-------------|-------|
| `!ping` | Check bot latency | `!ping` |
| `!help` | Show help | `!help command_name` |
| `!stats` | Show bot stats | `!stats` |
| `!uptime` | Bot uptime | `!uptime` |

---

## Troubleshooting

### Common Issues & Solutions

#### Database Connection Failed

**Problem:** `ConnectionError: Unable to connect to database`

**Solution:**
```bash
# Check database server status
sudo systemctl status postgresql

# Verify connection string
# Check firewall rules
sudo ufw allow 5432/tcp

# Test connection
psql -h localhost -U bot_user -d dhanworks_bot
```

#### Bot Not Responding

**Problem:** Bot doesn't respond to commands

**Solution:**
```python
# Check bot permissions
# Verify bot token
# Check command prefix
# Ensure bot has necessary intents
config.INTENTS = discord.Intents.default()
config.INTENTS.message_content = True

# Restart bot
# Check logs: tail -f logs/bot.log
```

#### Memory Leak

**Problem:** Bot memory usage increasing over time

**Solution:**
```python
# Clear cache periodically
import gc
gc.collect()

# Monitor memory usage
import tracemalloc
tracemalloc.start()

# Limit cache sizes
discord.utils.cached_slot_property
```

#### Rate Limiting

**Problem:** Bot hitting Discord rate limits

**Solution:**
```python
# Add delays between operations
import asyncio
await asyncio.sleep(1)

# Use batch operations
# Implement queue system
# Space out scheduled tasks
```

---

## API Endpoints

### User API

```
GET    /api/users              - List all users
GET    /api/users/{id}         - Get user by ID
POST   /api/users              - Create new user
PUT    /api/users/{id}         - Update user
DELETE /api/users/{id}         - Delete user
POST   /api/users/{id}/roles   - Assign role
```

### Bot API

```
GET    /api/bot/status         - Get bot status
GET    /api/bot/stats          - Get bot statistics
POST   /api/bot/command        - Execute command
GET    /api/bot/logs           - Get bot logs
```

### Session API

```
POST   /api/sessions           - Create session
GET    /api/sessions/{token}   - Validate session
DELETE /api/sessions/{token}   - Logout
```

### Response Format

**Success Response:**
```json
{
  "success": true,
  "data": {...},
  "timestamp": "2025-12-27T07:17:56Z"
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Error message",
  "code": "ERROR_CODE",
  "timestamp": "2025-12-27T07:17:56Z"
}
```

---

## Configuration

### Environment Variables

```env
# Bot Configuration
BOT_TOKEN=your_discord_bot_token
BOT_PREFIX=!
BOT_STATUS=online

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=dhanworks_bot
DB_USER=bot_user
DB_PASSWORD=secure_password

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/bot.log

# Features
ENABLE_MUSIC=true
ENABLE_MODERATION=true
ENABLE_ECONOMY=false
```

---

## Resources

- [Discord.py Documentation](https://discordpy.readthedocs.io/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Bot Repository](https://github.com/colin2018/dhanworks-bot)
- [Issue Tracker](https://github.com/colin2018/dhanworks-bot/issues)

---

**For more help, see the main README.md or contact the development team.**
