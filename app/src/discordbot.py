import logging
from agent import graph
import discord
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage
from discord.ext import commands
import re
import os
from messagehistory import MessageHistory
from langchain_openai import ChatOpenAI
import asyncio
history = MessageHistory()
logger = logging.getLogger('discord')
intents = discord.Intents.default()
intents.message_content = True

subhan_meme_SYSTEM_PROMPT = """You are a chatbot acting like the user "subhanafz" on Discord. You will respond to questions by emulating this user's style. Use the original user's question to guide your response better and maintain the persona throughout."""
subhan_meme_model = ChatOpenAI(model="ft:gpt-4o-mini-2024-07-18:personal:subhan-test3:Ay1oDmLB")

async def memify(question, prompt):
    message = f"Question: {question}\nPrompt: {prompt}"
    answer =  await subhan_meme_model.ainvoke([SystemMessage(content=subhan_meme_SYSTEM_PROMPT), HumanMessage(content=message)])
    return answer

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
        logger.info(await history.get_history())
        await history.add_message(HumanMessage(content=new_msg))
        history_length = len(await history.get_history())-1
        output = await graph.ainvoke({"messages": await history.get_history()})

        memed_output = await memify(cleaned_content, output["messages"][-1].content)
        for m in memed_output.content.splitlines():
            await message.channel.send(m)
            await asyncio.sleep(1)

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