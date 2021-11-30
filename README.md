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

#### Mime Type Filtering
`%types [list|<empty>]` - list current filters on allowed mime list
`%types add [channel]` - add filter to allowed mime list
`%types remove [channel]` - remove filter from allowed mime list

Mime filters are regex, so you can allow broad categories such as `video/*` for all video files; 
or you can be much more specific and specify `video/mp4` to only allow mp4 video.

For a full list of mime types and categories, go to: [https://www.iana.org/assignments/media-types/media-types.xhtml](https://www.iana.org/assignments/media-types/media-types.xhtml)

Click here: https://discord.com/api/oauth2/authorize?client_id=914259508203782195&permissions=274877918272&scope=bot to add to your server
