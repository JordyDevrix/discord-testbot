from lethal_functions import OpenNewQuestion
import discord
from discord.ext import commands, tasks


class VerkeerButton(discord.ui.Button):
    def __init__(self, option, ctx):
        self.ctx: commands.Context = ctx
        super().__init__(label=option, style=discord.ButtonStyle.primary)

    async def callback(self, interaction):
        if self.label == self.view.answer:
            await interaction.response.send_message(f"Goedzo {interaction.user.mention}")
        else:
            await interaction.response.send_message(f"{interaction.user.mention} Kut kind, ga leren ofz...")


class VolgendeButton(discord.ui.Button):
    def __init__(self, option, ctx):
        self.ctx: commands.Context = ctx
        super().__init__(label=option, style=discord.ButtonStyle.green)

    async def callback(self, interaction):
        if self.view.typ == "verkeersborden":
            quest = OpenNewQuestion.get_new_bord()
            question = quest[1]
            picture_name = question["naam"]
            picture_path = discord.File(f"{quest[0]}/{picture_name}.png", filename="output.png")
            titler = "Borden"
        else:
            quest = OpenNewQuestion.get_new_situatie()
            question = quest[1]
            picture_name = question["naam"]
            picture_path = discord.File(f"{quest[0]}/{picture_name}.jpg", filename="output.png")
            titler = "Situaties"

        vraag = question["vraag"]
        embed = discord.Embed(title=titler, color=discord.Color(int('ffc800', 16)))
        embed.add_field(name=f"{vraag} | `{picture_name}`", value="click op het juiste antwoord", inline=True)
        embed.set_image(url=f"attachment://output.png")
        await interaction.response.send_message(
            embed=embed,
            file=picture_path,
            view=VerkeerView(options=question["options"],
                             answer=question["answer"],
                             ctx=self.ctx,
                             typ=quest[0])
        )


class VerkeerView(discord.ui.View):
    def __init__(self, options, answer, ctx, typ):
        super().__init__()
        self.answer = answer
        self.typ = typ
        for option in options:
            try:
                self.add_item(VerkeerButton(option, ctx))
            except Exception as e:
                print(e)
        self.add_item(VolgendeButton("Next", ctx))
