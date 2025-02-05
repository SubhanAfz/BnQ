import logging
from agent import graph
import discord
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage
from discord.ext import commands
import re
import os
from messagehistory import MessageHistory

history = MessageHistory()
logger = logging.getLogger('discord')
intents = discord.Intents.default()
intents.message_content = True


bot = commands.Bot(command_prefix='?', intents=intents)
@bot.event
async def on_ready():
    logger.info(f'{bot.user} has connected to Discord!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if bot.user in message.mentions:
        logger.info("mentioned!!")
        cleaned_content = re.sub(r"<@!?\d+>", "", message.content).strip()

        new_msg = f'{message.author.name}: {cleaned_content}'

        logger.info(cleaned_content)
        await history.add_message(HumanMessage(content=new_msg))
        history_length = len(await history.get_history())-1
        output = await graph.ainvoke({"messages": await history.get_history()})
        
        await message.channel.send(output["messages"][-1].content)

        new_messages = output["messages"][history_length:]
        i = 0
        while i < len(new_messages):
            msg = new_messages[i]
            if isinstance(msg, AIMessage) and msg.tool_calls:
                if i + 1 < len(new_messages) and isinstance(new_messages[i + 1], ToolMessage):
                    grouped = (msg, new_messages[i + 1])
                    await history.add_message(grouped)
                    logger.info(f"Added grouped AI and Tool message: {type(msg).__name__} and {type(new_messages[i + 1]).__name__}")
                    i += 2
                    continue
            elif isinstance(msg, SystemMessage):
                continue
            await history.add_message(msg)
            logger.info(f"Added message: {type(msg).__name__}")
            i += 1
        

        
        logger.info(f'length: {len(await history.get_history())-1}')
        logger.info(f'history: {await history.get_history()}')
    await bot.process_commands(message)


bot.run(os.environ['DISCORD_BOT_TOKEN'])