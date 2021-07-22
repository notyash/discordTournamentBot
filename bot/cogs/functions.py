import discord
import pandas as pd
from discord.ext import commands
from discord.utils import get


class Functions(commands.Cog):
    def __init__(self, bot):

        self.googleSheetId = "1WLxOIVf8J9SqZBFp0rwhdMFgBrdaae189xASBYhLmbw"
        self.worksheetName = "discord_bot"
        self.URL = f"https://docs.google.com/spreadsheets/d/{self.googleSheetId}/gviz/tq?tqx=out:csv&sheet={self.worksheetName}"

        self.bot = bot

    async def create_channel(self, c_name, *, guild, overwrites, category):
        await guild.create_text_channel(name=c_name, overwrites=overwrites, category=category)
        print(f"Channel created: {c_name}")

    async def create_role_func(self, guild, *, r_name):
        role = await guild.create_role(name=f"{r_name} Role")
        if role:
            print(f"Role created: {r_name}")
            return role

    async def give_role(self, member: discord.Member, role):
        await member.add_roles(role)
        print(f"Role assigned to: {member.display_name}")

    async def assign_role(self, role, df, name, ctx):
        e = discord.Embed()
        result_id = []
        unreachable_users = []
        # gets index of row
        index, = df.index[df["channel_name"] == name]
        # if multiple member ids are given
        if len(df.index) > 0:
            try:
                result_id = df.loc[index, 'member_ids'].split(", ")
                for i in range(0, len(result_id)):
                    result_id[i] = int(result_id[i])
            except:
                pass
        # if only single member id is provided
        else:
            result_id = int(df.loc[index, 'member_ids'])

        for result in result_id:
            try:
                member = ctx.guild.get_member(result)
                if get(member.roles, id=role.id):
                    continue
                await self.give_role(member=member, role=role)
                e.description = f"You have been assigned **{role}** \n" \
                                f"Check **{name}** channel under the ***TOURNAMENT*** category for" \
                                f" updates on the tourney."
                await member.send(embed=e)
            # if member has dm off or if they are not in the server
            except:
                unreachable_users.append(result)
            result_id.clear()

        if unreachable_users:
            while "" in unreachable_users:
                unreachable_users.remove("")
            users_string = ' '.join(str(x) for x in unreachable_users).split(" ")
            e.description = f"Member(s) with this id: **{', '.join(x for x in users_string)}" \
                            f"** are not reachable."
            await ctx.send(embed=e)

    async def get_data_from_db(self):
        names = []
        # keep_default_na = False, to reject nan values
        df = pd.read_csv(self.URL, keep_default_na=False)

        for number in range(len(df.index)):
            # gets channel names from the column channel_name in the db
            channel_name = df.loc[number, 'channel_name']
            if "" == channel_name:
                continue
            names.append(channel_name)

        return names, df

    @commands.command(name="start", aliases=["create-channels"])
    @commands.has_permissions(administrator=True)
    async def start_bot(self, ctx):
        e = discord.Embed()
        e.description = "Functions started."
        await ctx.send(embed=e)
        names, df = await self.get_data_from_db()

        guild = ctx.message.guild

        for name in names:
            if role := get(guild.roles, name=f"{name} Role"):
                e.description = f"Skipping **{name}** because there is already a channel with same name."
                await ctx.send(embed=e)
                await self.assign_role(role=role, name=name, df=df, ctx=ctx)
                continue

            role = await self.create_role_func(guild=guild, r_name=name)
            category = discord.utils.get(guild.categories, name="TOURNAMENTS")

            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                guild.me: discord.PermissionOverwrite(read_messages=True),
                role: discord.PermissionOverwrite(read_messages=True)
            }

            # checks if there is another channel with same name
            if not get(guild.channels, name=name.lower()):
                await self.create_channel(guild=guild, c_name=name, overwrites=overwrites, category=category)
                # sends message after all channels are created
                if name == names[len(names) - 1]:
                    e.description = f"Channels created: {', '.join(x for x in names)}"
                    await ctx.send(embed=e)

            await self.assign_role(role=role, name=name, df=df, ctx=ctx)

        e.description = 'Functions are completed.'
        msg = await ctx.send(embed=e)
        await msg.add_reaction("✅")


def setup(bot):
    bot.add_cog(Functions(bot))
