# Integration Guide - Dhanworks Bot

## Overview

This guide provides comprehensive instructions for integrating the Dhanworks Bot into your Discord server and configuring it for optimal performance. The Dhanworks Bot is a feature-rich Discord bot designed to enhance server management, moderation, and user engagement.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Core Features](#core-features)
5. [Command Reference](#command-reference)
6. [Advanced Setup](#advanced-setup)
7. [Troubleshooting](#troubleshooting)
8. [API Integration](#api-integration)
9. [Security Best Practices](#security-best-practices)
10. [Support & Resources](#support--resources)

## Prerequisites

Before integrating the Dhanworks Bot, ensure you have:

- **Discord Server Admin Access**: You must be a server administrator to add bots
- **Discord Account**: An active Discord account with appropriate permissions
- **Bot Token**: Obtain the bot token from the [Discord Developer Portal](https://discord.com/developers/applications)
- **Python 3.8+** (if self-hosting): Required for running the bot locally
- **Basic Command Knowledge**: Familiarity with Discord commands and permissions

### Required Permissions

The bot requires the following Discord permissions:

- **General Permissions**
  - Read Messages/View Channels
  - Send Messages
  - Manage Messages
  - Embed Links

- **Moderation Permissions**
  - Kick Members
  - Ban Members
  - Manage Roles
  - Manage Channels

- **Advanced Permissions**
  - Manage Guild
  - Administrator (optional, for full functionality)

## Installation

### Step 1: Create the Bot Application

1. Visit [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and name it "Dhanworks Bot"
3. Navigate to the "Bot" section
4. Click "Add Bot"
5. Copy your bot token (store it securely, never share it)

### Step 2: Configure Bot Permissions

1. Go to "OAuth2" → "URL Generator"
2. Select scopes: `bot`
3. Select permissions:
   - Read Messages/View Channels
   - Send Messages
   - Manage Messages
   - Embed Links
   - Kick Members
   - Ban Members
   - Manage Roles
   - Manage Channels
4. Copy the generated URL and open it in your browser
5. Select your server and authorize the bot

### Step 3: Add Bot to Your Server

1. Use the OAuth2 URL generated in Step 2
2. Select your target server from the dropdown
3. Confirm the permissions
4. Click "Authorize"

The bot should now appear in your server's member list!

## Configuration

### Initial Setup

After adding the bot to your server, complete the following setup steps:

#### 1. Set Default Prefix

```
/setprefix <prefix>
```

Example:
```
/setprefix !
```

#### 2. Configure Role Assignments

```
/setrole <role_name>
```

#### 3. Set Logging Channel

```
/setlogchannel #logs
```

This channel will receive logs for all moderation actions.

#### 4. Configure Welcome Messages

```
/setwelcome #channel "Your welcome message here"
```

### Environment Variables

If self-hosting, create a `.env` file in the root directory:

```env
DISCORD_TOKEN=your_bot_token_here
DATABASE_URL=your_database_url
BOT_PREFIX=!
LOG_LEVEL=INFO
ENVIRONMENT=production
```

**⚠️ Security Warning**: Never commit the `.env` file to version control. Add it to `.gitignore`.

## Core Features

### 1. Moderation Tools

- **Kick/Ban Users**: Remove disruptive members from your server
- **Mute/Unmute**: Temporary member restrictions
- **Warn System**: Track member violations
- **Auto-moderation**: Automatic response to prohibited content

### 2. Server Management

- **Role Management**: Automatic role assignment and management
- **Channel Management**: Create, delete, and organize channels
- **Message Management**: Bulk delete, pin/unpin messages
- **Server Settings**: Customize bot behavior per server

### 3. User Engagement

- **Leveling System**: Track member activity and assign ranks
- **Reaction Roles**: Allow members to self-assign roles
- **Custom Commands**: Create server-specific commands
- **Announcements**: Schedule and send automated messages

### 4. Utility Features

- **Help Commands**: Comprehensive command documentation
- **User Info**: Display detailed user profiles
- **Server Info**: Show server statistics and information
- **Statistics**: Track server activity and growth

## Command Reference

### Moderation Commands

```
!kick <user> [reason]          - Kick a user from the server
!ban <user> [reason]           - Ban a user permanently
!mute <user> <time>            - Mute a user for specified duration
!unmute <user>                 - Unmute a previously muted user
!warn <user> <reason>          - Warn a user
!warnings <user>               - Check user warnings
!clearwarnings <user>          - Clear all warnings for a user
```

### Server Management Commands

```
!prefix <new_prefix>           - Change bot prefix
!setlogchannel <channel>       - Set logging channel
!setwelcome <channel> <msg>    - Configure welcome message
!announce <channel> <message>  - Make an announcement
!settings                      - View current server settings
```

### User Commands

```
!help [command]                - Show help information
!userinfo [user]               - Display user information
!serverinfo                    - Show server statistics
!stats                         - Display member statistics
!profile [user]                - View user profile
```

### Utility Commands

```
!ping                          - Check bot latency
!uptime                        - Display bot uptime
!invite                        - Get bot invite link
!support                       - Get support server link
!suggest <suggestion>          - Submit a suggestion
```

## Advanced Setup

### Database Configuration

The bot supports multiple database backends. Configure your database:

```env
# PostgreSQL (Recommended)
DATABASE_URL=postgresql://user:password@localhost:5432/dhanworks

# MongoDB
DATABASE_URL=mongodb+srv://user:password@cluster.mongodb.net/dhanworks

# SQLite (Development)
DATABASE_URL=sqlite:///./dhanworks.db
```

### Custom Role Groups

Create role groups for easier management:

```
/rolegroup create <group_name> <roles>
/rolegroup add <group_name> <role>
/rolegroup remove <group_name> <role>
/rolegroup list
```

### Automated Tasks

Set up automated tasks and schedules:

```
/schedule <time> <command>     - Schedule a command for specific time
/repeat <interval> <command>   - Repeat a command at intervals
/tasks                         - View all scheduled tasks
```

### Webhook Integration

Integrate external services via webhooks:

```
/webhook create <service_name>
/webhook list
/webhook delete <webhook_id>
```

## Troubleshooting

### Bot Not Responding

**Issue**: Bot doesn't respond to commands

**Solutions**:
1. Verify the bot is online (check member list)
2. Check that you're using the correct prefix
3. Ensure the bot has permission to view and send messages in the channel
4. Restart the bot application
5. Check server status on Discord's status page

### Permission Errors

**Issue**: "Missing Permissions" error

**Solutions**:
1. Go to Server Settings → Roles
2. Ensure the bot's role is positioned above other roles
3. Grant the bot role necessary permissions
4. Verify command permissions: `/perms <command>`

### Database Connection Issues

**Issue**: Database connection timeout

**Solutions**:
1. Verify `DATABASE_URL` is correct in `.env`
2. Check database server status and availability
3. Verify network connectivity and firewall rules
4. Review database logs for specific errors
5. Ensure database credentials are valid

### Command Not Found

**Issue**: Command returns "Unknown command"

**Solutions**:
1. Verify correct spelling and prefix
2. Check if command is enabled: `/cmd enable <command>`
3. Ensure you have permission to use the command
4. Update bot to latest version
5. Check command aliases with `/help`

## API Integration

### RESTful API Endpoints

The bot exposes several API endpoints for integration:

#### Authentication

All API requests require a Bearer token:

```
Authorization: Bearer <api_token>
```

#### Endpoints

**Get Server Info**
```
GET /api/v1/servers/{server_id}
```

**Get User Info**
```
GET /api/v1/users/{user_id}
```

**Get Member List**
```
GET /api/v1/servers/{server_id}/members
```

**Create Custom Command**
```
POST /api/v1/servers/{server_id}/commands
Content-Type: application/json

{
  "name": "command_name",
  "response": "command response",
  "permissions": ["@everyone"]
}
```

**Log Event**
```
POST /api/v1/servers/{server_id}/logs
Content-Type: application/json

{
  "event_type": "moderation",
  "user_id": "123456789",
  "action": "kick",
  "reason": "violation"
}
```

### Webhook Events

Subscribe to bot events via webhooks:

#### Supported Events

- `user.join` - User joins server
- `user.leave` - User leaves server
- `message.delete` - Message deleted
- `moderation.action` - Moderation action taken
- `role.assigned` - Role assigned to user
- `role.removed` - Role removed from user

#### Webhook Payload Example

```json
{
  "event": "moderation.action",
  "timestamp": "2025-12-27T07:09:29Z",
  "server_id": "123456789",
  "user_id": "987654321",
  "action": "kick",
  "reason": "Rule violation",
  "moderator_id": "111111111"
}
```

## Security Best Practices

### Protecting Your Bot Token

1. **Never Share**: Keep your bot token completely secret
2. **Environment Variables**: Store tokens in `.env` files
3. **Rotate Regularly**: Regenerate tokens periodically
4. **Restrict Access**: Limit who has access to token files
5. **Use Secrets Management**: For production, use services like HashiCorp Vault

### Server Security

1. **Role Hierarchy**: Ensure the bot's role is appropriately positioned
2. **Permission Auditing**: Regularly review bot permissions
3. **Logging**: Enable logging for all moderation actions
4. **Rate Limiting**: The bot implements rate limiting to prevent abuse
5. **Audit Log**: Monitor the Discord audit log for bot actions

### Data Protection

1. **GDPR Compliance**: Respect user privacy regulations
2. **Data Retention**: Configure how long data is retained
3. **User Consent**: Obtain consent before storing user data
4. **Encryption**: Sensitive data is encrypted at rest
5. **Access Control**: Restrict data access to authorized personnel

### Update Management

1. **Stay Current**: Regularly update to the latest bot version
2. **Security Patches**: Apply security updates immediately
3. **Change Logs**: Review changes before updating
4. **Testing**: Test updates in a development server first
5. **Rollback Plan**: Maintain ability to rollback if issues occur

## Support & Resources

### Documentation

- [Full Command Documentation](./docs/COMMANDS.md)
- [Configuration Guide](./docs/CONFIG.md)
- [API Documentation](./docs/API.md)
- [Troubleshooting Guide](./docs/TROUBLESHOOTING.md)

### Community

- **Support Server**: [Join Discord Server](https://discord.gg/dhanworks)
- **GitHub Issues**: [Report Issues](https://github.com/colin2018/dhanworks-bot/issues)
- **Feature Requests**: [Request Features](https://github.com/colin2018/dhanworks-bot/discussions)
- **Discussions**: [Community Forum](https://github.com/colin2018/dhanworks-bot/discussions)

### Getting Help

1. Check the [FAQ](./docs/FAQ.md)
2. Search [existing issues](https://github.com/colin2018/dhanworks-bot/issues)
3. Post in the support server
4. Create a detailed bug report with:
   - Bot version
   - Error messages
   - Steps to reproduce
   - Server configuration
   - Relevant logs

### Contributing

We welcome contributions! See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

---

## Version Information

- **Current Version**: 2.0.0
- **Last Updated**: 2025-12-27
- **Compatibility**: Discord.py 2.0+, Python 3.8+

## License

This bot is licensed under the MIT License. See [LICENSE](./LICENSE) for details.

---

For questions or issues, please visit our [support server](https://discord.gg/dhanworks) or open an issue on [GitHub](https://github.com/colin2018/dhanworks-bot/issues).
