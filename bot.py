DISCORD_TOKEN= "ใส่โทเคนในนี้"
CHANNEL_ID = 1561755779823042722

import discord
from datetime import date
from discord.ext import commands

import tracker

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


@bot.command(name="spend")
async def spend(ctx, price: float, *, details: str):
    """Log an expense.  !spend 5.00 Coffee   or   !spend 5.00 Iced Coffee | Food"""
    if price <= 0:
        await ctx.send("Price must be greater than 0.")
        return

    if "|" in details:
        item, category = (part.strip() for part in details.split("|", 1))
    else:
        item, category = details.strip(), "Other"

    if not item:
        await ctx.send("Please include an item name, e.g. `!spend 5.00 Coffee`")
        return
    category = category or "Other"

    tracker.add_expense(item, price, category)
    await ctx.send(f"Saved: **{item}**, {price:.2f} [{category}]")


@spend.error
async def spend_error(ctx, error):
    if isinstance(error, (commands.BadArgument, commands.MissingRequiredArgument)):
        await ctx.send(
            "Usage: `!spend <price> <item>` or `!spend <price> <item> | <category>`\n"
            "Example: `!spend 5.00 Coffee` or `!spend 12.50 Lunch | Food`"
        )
    else:
        raise error


@bot.command(name="week")
async def week(ctx):
    """Total spending over the last 7 days."""
    await ctx.send(f"Last 7 days: **{tracker.weekly_total():.2f}**")


@bot.command(name="month")
async def month(ctx):
    """Total spending this month."""
    await ctx.send(f"This month: **{tracker.monthly_total():.2f}**")


@bot.command(name="categories")
async def categories(ctx):
    """Spending per category this month."""
    today = date.today()
    totals = tracker.category_breakdown(today.replace(day=1), today)
    if not totals:
        await ctx.send("No expenses logged this month yet.")
        return
    lines = [
        f"{cat}: {amount:.2f}"
        for cat, amount in sorted(totals.items(), key=lambda kv: kv[1], reverse=True)
    ]
    await ctx.send("**This month by category**\n" + "\n".join(lines))


@bot.command(name="recent")
async def recent(ctx, count: int = 5):
    """Show your most recent entries.  !recent 10"""
    count = max(1, min(count, 20))
    entries = tracker.load_expenses()[-count:]
    if not entries:
        await ctx.send("No expenses logged yet.")
        return
    lines = [
        f"{e['date']}  {e['item']}  {e['price']:.2f}  [{e['category']}]"
        for e in reversed(entries)
    ]
    await ctx.send("**Recent entries**\n" + "\n".join(lines))



if __name__ == "__main__":
    if not DISCORD_TOKEN or DISCORD_TOKEN == "PASTE_YOUR_BOT_TOKEN_HERE":
        raise SystemExit("Please set your Discord bot token in bot.py.")

    bot.run(DISCORD_TOKEN)
