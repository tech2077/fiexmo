# fiexmo - File type and Extension Moderation

## a Discord bot to deal with unsafe files

### Commands

#### Mode
`%mode` - show current mode

`%mode [OFF|AUTOFLAG|AUTODELETE]` - set current mode

#### Channel Ignoring
`%ignore list` - list current channels being ignored
`%ignore add [channel]` - add channel to ignore list
`%ignore remove [channel]` - remove channel from ignore list

#### Roles
`%ignore list` - list current roles on role list
`%ignore add [channel]` - add role to role list
`%ignore remove [channel]` - remove role from role list

#### Note about roles

by default the bot will listen to any user when first joining.
be sure to add roles after adding to bot in order to prevent regular
users from modifying settings.