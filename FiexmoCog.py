import logging
import re
from typing import List

import aiohttp
import discord
import magic
from discord.ext import commands

from Settings import FiexmoSettingStore, ModMode


class FiexmoCog(commands.Cog):
    def __init__(self, bot_, settings_store: FiexmoSettingStore, logger: logging.Logger, approved_mimes: List[str]):
        self.bot = bot_
        self._last_member = None
        self.settings_store = settings_store
        self.logger = logger
        self.approved_mimes = approved_mimes

    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.log(level=logging.INFO, msg=f'{self.bot.user} has connected to Discord!')

    async def auto_flag(self, msg, file_approved: bool):
        if file_approved:
            await msg.add_reaction('\N{White Heavy Check Mark}')
        else:
            await msg.add_reaction('\N{Cross Mark}')

    async def auto_delete(self, msg, file_approved: bool, name: str):
        if file_approved:
            pass  # do nothing with approved files
        else:
            await msg.delete()
            await msg.channel.send(f"Message removed for potentially dangerous attachment: {name}")

    @commands.Cog.listener()
    async def on_message(self, message):
        # ignore messages from this user
        if message.author == self.bot.user:
            return

        setting = self.settings_store.get(message.guild.id)

        # only check if there is an attachment or we have moderation configured
        if len(message.attachments) > 0 and \
                setting.mode != ModMode.OFF and \
                message.channel.id not in setting.ignores:
            for a in message.attachments:
                name = a.filename
                url = a.url
                # download the file to test the magic number
                # use range to get only first up to 511 bytes to validate magic number
                async with aiohttp.ClientSession(headers={"Range": "bytes=0-511"}) as session:
                    async with session.get(url) as resp:
                        if resp.status == 200 or resp.status == 206:
                            data = await resp.read()
                            mime = magic.from_buffer(data, mime=True)

                            self.logger.log(level=logging.DEBUG, msg=f'{name} {len(data)} {mime} {url} {resp.status}')

                            file_approved = any([re.match(mime_regex, mime) for mime_regex in setting.allowed_mimes])
                            if setting.mode == ModMode.AUTOFLAG:
                                await self.auto_flag(message, file_approved)
                            else:
                                await self.auto_delete(message, file_approved, name)

    @commands.command()
    async def mode(self, ctx, mode: str = None, member: discord.Member = None):
        self.logger.log(level=logging.DEBUG, msg=f"guild: {ctx.guild}:{ctx.guild.id} {ctx.channel}:{ctx.channel.id}")
        setting = self.settings_store.get(ctx.guild.id)
        author_roles = ctx.author.roles

        if len(setting.use_roles) > 0 and \
                not any([discord.utils.get(ctx.guild.roles, id=rid) in author_roles for rid in setting.use_roles]):
            return

        if mode is None:
            await ctx.send(f"Current mode for {ctx.guild} is {str(setting.mode)}")
        else:
            try:
                setting.mode = ModMode[mode]

                self.settings_store.set(ctx.guild.id, setting)
            except KeyError as e:
                self.logger.log(level=logging.INFO, msg=f"{e}")

                await ctx.send(f"Invalid Mode Name: {mode}")

    @commands.command()
    async def ignore(self, ctx, op: str, channel: str = None, member: discord.Member = None):
        """
        Command to manipulate ignore list for server. Has three commands: list, add, remove.
        list shows the current channels being ignored
        add adds to the ignore list
        remove removes from the ignore list

        :param ctx:
        :param op:
        :param channel:
        :param member:
        """
        self.logger.log(level=logging.INFO, msg=f"guild: {ctx.guild}:{ctx.guild.id} {ctx.channel}:{ctx.channel.id}")
        setting = self.settings_store.get(ctx.guild.id)
        author_roles = ctx.author.roles

        if len(setting.use_roles) > 0 and \
                not any([discord.utils.get(ctx.guild.roles, id=rid) in author_roles for rid in setting.use_roles]):
            return

        if op == "list" or op is None or channel is None:
            self.logger.log(level=logging.DEBUG, msg=setting.ignores)

            ignore_name_list = [f"#{ctx.guild.get_channel(ch).name}" for ch in setting.ignores]

            await ctx.send(f"Current ignores for {ctx.guild} are {ignore_name_list}")
        elif op == "add" and channel is not None:
            try:
                channel = discord.utils.get(ctx.guild.channels, name=channel)
                channel_id = channel.id

                if channel_id not in setting.ignores:
                    setting.ignores.append(channel_id)

                self.settings_store.set(ctx.guild.id, setting)

                ignore_name_list = [f"#{ctx.guild.get_channel(ch).name}" for ch in setting.ignores]
                await ctx.send(f"Channel {channel} added to ignore list: {ignore_name_list}")
            except KeyError as e:
                self.logger.log(level=logging.INFO, msg=f"{e}")

                await ctx.send(f"Invalid Channel Name: {channel}")
        elif op == "remove" and channel is not None:
            try:
                channel = discord.utils.get(ctx.guild.channels, name=channel)
                channel_id = channel.id

                if channel_id in setting.ignores:
                    setting.ignores.remove(channel_id)

                self.settings_store.set(ctx.guild.id, setting)

                ignore_name_list = [f"#{ctx.guild.get_channel(ch).name}" for ch in setting.ignores]
                await ctx.send(f"Channel {channel} removed from ignore list: {ignore_name_list}")
            except KeyError as e:
                self.logger.log(level=logging.INFO, msg=f"{e}")

                await ctx.send(f"Invalid Channel Name: {channel}")

    @commands.command()
    async def roles(self, ctx, op: str, role: str = None, member: discord.Member = None):
        """
        Command to manipulate role list for server. Has three commands: list, add, remove.
        list: shows the current roles allowed to use the bot
        add: adds to the role list
        remove: removes from the role list

        :param ctx:
        :param op:
        :param role:
        :param member:
        """
        self.logger.log(level=logging.INFO, msg=f"guild: {ctx.guild}:{ctx.guild.id} {ctx.channel}:{ctx.channel.id}")
        setting = self.settings_store.get(ctx.guild.id)
        author_roles = ctx.author.roles

        if len(setting.use_roles) > 0 and \
                not any([discord.utils.get(ctx.guild.roles, id=rid) in author_roles for rid in setting.use_roles]):
            return

        if op == "list" or op is None or role is None:
            self.logger.log(level=logging.DEBUG, msg=setting.ignores)

            role_name_list = [f"{ctx.guild.get_role(r)}" for r in setting.use_roles]

            await ctx.send(f"Current fiexmo roles for {ctx.guild} are {role_name_list}")
        elif op == "add" and role is not None:
            try:
                role = discord.utils.get(ctx.guild.roles, name=role)
                role_id = role.id

                if role_id not in setting.use_roles:
                    setting.use_roles.append(role_id)

                self.settings_store.set(ctx.guild.id, setting)

                role_name_list = [f"{ctx.guild.get_role(r)}" for r in setting.use_roles]
                await ctx.send(f"Role {role} added to role list: {role_name_list}")
            except KeyError as e:
                self.logger.log(level=logging.INFO, msg=f"{e}")

                await ctx.send(f"Invalid Role Name: {role}")
        elif op == "remove" and role is not None:
            try:
                role = discord.utils.get(ctx.guild.roles, name=role)
                role_id = role.id

                if role_id in setting.use_roles:
                    setting.use_roles.remove(role_id)

                self.settings_store.set(ctx.guild.id, setting)

                role_name_list = [f"{ctx.guild.get_role(r)}" for r in setting.use_roles]
                await ctx.send(f"Role {role} removed from role list: {role_name_list}")
            except KeyError as e:
                self.logger.log(level=logging.INFO, msg=f"{e}")

                await ctx.send(f"Invalid Role Name: {role}")

    @commands.command()
    async def types(self, ctx, op: str = None, mime: str = None, member: discord.Member = None):
        self.logger.log(level=logging.INFO, msg=f"guild: {ctx.guild}:{ctx.guild.id} {ctx.channel}:{ctx.channel.id}")
        setting = self.settings_store.get(ctx.guild.id)
        author_roles = ctx.author.roles

        if len(setting.use_roles) > 0 and \
                not any([discord.utils.get(ctx.guild.roles, id=rid) in author_roles for rid in setting.use_roles]):
            return

        if op == "info" or op == "" or op is None:
            self.logger.log(level=logging.DEBUG, msg=setting.allowed_mimes)

            await ctx.send(f"Current allowed filetype mimes are: `{setting.allowed_mimes}`\n" +
                           "For additional information on mimes, visit: " +
                           "https://www.iana.org/assignments/media-types/media-types.xhtml")
        elif op == "add" and mime is not None:
            try:
                if mime not in setting.allowed_mimes:
                    setting.allowed_mimes.append(mime)

                self.settings_store.set(ctx.guild.id, setting)
                setting = self.settings_store.get(ctx.guild.id)

                await ctx.send(f"Mime filter {mime} added to ignore list: {setting.allowed_mimes}")
            except KeyError as e:
                self.logger.log(level=logging.INFO, msg=f"{e}")

                await ctx.send(f"Invalid Mime Filter: {mime}")
        elif op == "remove" and mime is not None:
            try:
                if mime in setting.allowed_mimes:
                    setting.allowed_mimes.remove(mime)

                self.settings_store.set(ctx.guild.id, setting)
                setting = self.settings_store.get(ctx.guild.id)

                await ctx.send(f"Mime filter {mime} removed from ignore list: {setting.allowed_mimes}")
            except KeyError as e:
                self.logger.log(level=logging.INFO, msg=f"{e}")

                await ctx.send(f"Invalid Mime Filter: {mime}")
