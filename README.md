# Modmail Role Blocker Plugin

This plugin prevents users with a specific role from opening new Modmail threads.

## Features
- Blocks users with a configurable role ID from initiating new Modmail threads.
- Sends an informative error message to the user if they are blocked.
- If the blocking role is removed, the user can open threads again.

## Installation
Use the following command in your Modmail server:
```
?plugin add breadybread123/role-blocker/role-blocker
```
*(Replace `?` with your bot's prefix)*

## Configuration
The `blocked_role_id` in `role-blocker.py` needs to be set to the ID of the role you wish to block.
