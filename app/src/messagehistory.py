from collections import deque
from langchain_core.messages import SystemMessage
import asyncio
import os
class MessageHistory:
    def __init__(self):
        self.messages = deque(maxlen=int(os.environ["MAX_CONTEXT_LENGTH"]))
        self.lock = asyncio.Lock()

        self.preprompt = SystemMessage(content="""
            You are a helpful and direct Discord chatbot. Users will ask you questions, and you must reply with a concise answer that addresses only the user's question.

            Format:
            - User messages are prefixed with their name (e.g., "John: What is my name?").
            - Your reply should be direct and should not repeat any part of the user's message.

            Rules:
            1. Answer only the question asked. Do not include extra information or repeat previously sent user messages.
            2. If the question involves current or recent information, use the provided tools to search for up-to-date details.
            3. When replying, focus solely on the question. Do not reference or include details from prior messages unless absolutely necessary.
            4. If a user asks where your code is hosted, reply with: "https://github.com/SubhanAfz/QnB/"
            5. When a user mentions another person, the mention will appear in this format: `<@user_id>` (where `user_id` is a number).
            6. Each message may include extra context (such as the sender's username and the Guild ID). Ignore the sender’s username for your answer, but if the user’s question is about the Discord server or its details, you are allowed to use the Guild ID to retrieve that information.

            Example Interaction:
            User: "John: What is my name?"
            Your Reply: "Your name is John."

            Remember, be direct, concise, and answer only what is asked.
        """, additional_kwargs={"__openai_role__": "developer"})
    async def add_message(self, message):
        async with self.lock:
            self.messages.append(message)
    async def get_history(self):
        async with self.lock:
            flattened = []
            #flattened.append(self.preprompt)
            for unit in self.messages:
                if isinstance(unit, tuple):
                    flattened.extend(unit)
                else:
                    flattened.append(unit)
            return flattened