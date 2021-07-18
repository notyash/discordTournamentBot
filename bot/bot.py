from pathlib import Path

import discord
from discord.errors import Forbidden
from discord.ext import commands
from discord.ext.commands import CommandNotFound, Context

IGNORE_EXCEPTIONS = (CommandNotFound,)


class MyBot(commands.Bot):
    def __init__(self):
        self.ready = False
        self._cogs = [p.stem for p in Path(".").glob("./bot/cogs/*.py")]
        super().__init__(
            command_prefix=self.prefix,
            case_insensitive=True,
            intents=discord.Intents.all())

    def setup(self):
        print("Running setup")

        for cog in self._cogs:
            self.load_extension(f"bot.cogs.{cog}")
            print(f"Loaded cog {cog}.")

        print("Setup complete.")

    def run(self):
        self.setup()

        with open("data/token.0", "r", encoding="utf-8") as f:
            TOKEN = f.read()

        print("Running bot....")
        super().run(TOKEN, reconnect=True)

    async def shutdown(self):
        print("Shutting down.")
        await super().close()

    async def close(self):
        print("Closing...")
        await self.shutdown()

    async def on_connect(self):
        print("bot connected.")

    async def on_resumed(self):
        print("bot resumed.")

    async def on_disconnect(self):
        print("bot disconnected.")

    async def on_error(self, err, *args, **kwargs):
        if err == "on_command_error":
            await args[0].send("Something went wrong.")

        raise

    async def on_command_error(self, ctx, exc):
        if any([isinstance(exc, error) for error in IGNORE_EXCEPTIONS]):
            pass

        elif hasattr(exc, "original"):
            # if isinstance(exc.original, HTTPException):
            # 	await ctx.send("Unable to send message.")

            if isinstance(exc.original, Forbidden):
                await ctx.send("I do not have permission to do that.")

            else:
                raise exc.original

        else:
            raise exc

    async def on_ready(self):
        self.ready = True
        print("READY.")

    async def prefix(self, bot, msg):
        return commands.when_mentioned_or("!")(bot, msg)

    async def process_commands(self, message):
        ctx = await self.get_context(message, cls=Context)

        if ctx.command is not None and ctx.guild is not None:
            if not self.ready:
                await ctx.send("I'm not ready to receive commands. Please wait a few seconds.")

            else:
                await self.invoke(ctx)

    async def on_message(self, message):
        if not message.author.bot:
            await self.process_commands(message)
