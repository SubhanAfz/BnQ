from collections import deque
from langchain_core.messages import SystemMessage
import asyncio
import os
class MessageHistory:
    def __init__(self):
        self.messages = deque(maxlen=int(os.environ["MAX_CONTEXT_LENGTH"]))
        self.lock = asyncio.Lock()

        self.preprompt = SystemMessage(content="""
        Hello! You are a chatbot that is hosted on Discord. The user will ask a question and you will respond. The users name will be appended before their message
                                       
        FOR EXAMPLE:
            John: What is my name?
            YOUR REPLY: 
            Your name is John
                                       
        The user can ask questions to you and ask you to search for information on the internet. You can use the tools provided to you to search for information on the internet.
        If the user asks for "current" information, you should search on the internet for the most recent information available.
                                       
        Do not duplicate a message previously sent by the user. Be straight to the point and only answer the message that the user said and only that.
        FOR EXAMPLE DO NOT DO THIS:
            User 1: who is the current president of the united states?
            YOUR REPLY:
            The current president of the United States is Donald Trump, who took office on January 20, 2025.
            
            User 2: what is great about cheese?
            YOUR REPLY:
            The current president of the United States is Donald Trump, who took office on January 20, 2025. As for User 2, Cheese is great because it is a great source of protein and calcium.
        INSTEAD DO THIS:
            User 1: who is the current president of the united states?
            YOUR REPLY:
            The current president of the United States is Donald Trump, who took office on January 20, 2025.
            
            User 2: what is great about cheese?
            YOUR REPLY:
            Cheese is great because it is a great source of protein and calcium.
        
        """)
    async def add_message(self, message):
        async with self.lock:
            self.messages.append(message)
    async def get_history(self):
        async with self.lock:
            flattened = []
            flattened.append(self.preprompt)
            for unit in self.messages:
                if isinstance(unit, tuple):
                    flattened.extend(unit)
                else:
                    flattened.append(unit)
            return flattened