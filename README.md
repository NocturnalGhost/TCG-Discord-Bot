# Discord Verification Bot

## Overview
This project is a Discord verification bot designed to restrict server access to verified university students. It uses a two-step verification process:
1. Student ID validation
2. Email-based 6-digit verification code confirmation

Once verified, users are automatically assigned a role that grants access to the server.

## Features
- Automatic DM onboarding for new members
- Student ID validation (7-digit format)
- Automatic university email generation
- Email delivery of verification codes via SMTP
- 6-digit code verification system
- Role assignment upon successful verification
- Moderator logging of verified users
- Temporary in-memory session tracking

## Verification Flow
### 1. User Joins Server
When a user joins the server, the bot sends them a direct message:

Welcome to the server!
Please reply with your 7-digit Student ID.

### 2. Student ID Submission
The user replies with their Student ID.

Validation rules:
- Must be numeric
- Must be exactly 7 digits

If valid:
- A university email is generated:

up{student_id}@myport.ac.uk

- A 6-digit verification code is generated
- A verification session is stored in memory

### 3. Email Verification Code Sent
The bot sends an email containing the verification code:

Your verification code is: XXXXXX
Please return to Discord and enter this code.

SMTP is used to send emails via Gmail.

### 4. Code Submission
The user returns to Discord and submits the 6-digit code.

The bot checks the code against the stored session.

### 5. Successful Verification
If the code matches:

- The user is assigned the Verified role
- A log is sent to a private moderation channel
- The user is granted access to the server
- The verification session is deleted

Moderator log includes:
- Discord username
- Student ID (formatted as up1234567)

User message:
Verification successful. Access granted.

### 6. Failed Verification
If the code is incorrect:

The bot responds:
Incorrect code. Please try again or restart verification with your Student ID.

## System Architecture
User joins server
|
v
Bot sends DM (Student ID request)
|
v
User submits Student ID
|
v
Bot generates email + verification code
|
v
Email sent to university address
|
v
User submits verification code
|
v
Bot validates code
|
v
Role assigned + log created

## Configuration
The bot requires the following environment variables:

DISCORD_TOKEN
SENDER_EMAIL
SENDER_PASSWORD

## Required IDs (hardcoded or configurable)

- SERVER_ID: Discord server ID
- VERIFIED_ROLE_ID: Role assigned after verification
- LOG_CHANNEL_ID: Private moderator log channel

## Permissions Required
The bot requires the following Discord permissions:

- Read Messages
- Send Messages
- Send Direct Messages
- Manage Roles
- View Channels
- Read Message History

## Email Requirements
To send verification emails, the bot requires:

- Gmail account
- Google App Password enabled
- SMTP access via `aiosmtplib`

## Data Storage
Verification sessions are stored in memory:

pending_verifications = {
user_id: {
"student_id": "1234567",
"code": "482913"
}
}

### Important Notes:
- Data is not persistent
- Restarting the bot clears all sessions
- Users must restart verification after a restart

## Deployment (Azure Container Instances)
The bot is deployed using Docker and Azure Container Instances.

### Build Docker image:
docker build -t discord-verification-bot .

### Run locally:
docker run -e DISCORD_TOKEN=xxx -e SENDER_EMAIL=xxx -e SENDER_PASSWORD=xxx discord-verification-bot

### Deploy to Azure:
az container create
--resource-group Discord-Bots
--name discord-bot
--image yourdockerhubuser/discord-verification-bot:v1
--os-type Linux
--restart-policy Always
--environment-variables DISCORD_TOKEN="xxx" SENDER_EMAIL="xxx" SENDER_PASSWORD="xxx"

## Limitations
- No persistent storage (memory-based sessions only)
- No rate limiting (susceptible to spam)
- Email delivery depends on SMTP reliability
- Requires manual redeployment for updates
- No automatic retry system for failed emails

## Recommended Improvements
- Add database support (SQLite, Redis, or PostgreSQL)
- Add verification code expiration timer
- Add retry limits for incorrect codes
- Add rate limiting for Student ID submissions
- Add persistent session storage
- Add CI/CD pipeline for automatic deployment
