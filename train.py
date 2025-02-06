questions = ["What is 5 + 7",
"What is the square root of 16?",
"Solve for x: 2x + 3 = 7.",
"What is 15 divided by 3?",
"What is the value of π (pi) rounded to two decimal places?",
"What planet is known as the Red Planet?",
"What is the chemical symbol for water?",
"How many states of matter are there?",
"What force keeps us on the ground?",
"What is the largest organ in the human body?",
"What is the capital of France?",
"Which continent is Australia part of?",
"What is the longest river in the world?",
"What ocean is the largest?",
"How many continents are there?",
"Who was the first President of the United States?",
"What language is spoken in Brazil?",
"How many sides does a hexagon have?",
"What is the name of the fairy tale character who leaves a glass slipper behind?",
"How many hours are in a day?"]

system_prompt = """
        Hello! You are a chatbot, which is acting like the user subhanafz, and you're hosted on Discord. The user will ask a question and you will respond. The users name will be appended before their message
                                       
        FOR EXAMPLE:
            John: What is my name?
            YOUR REPLY: 
            Your name is John.
                                       
        The user can ask questions to you and ask you to search for information on the internet. You can use the tools provided to you to search for information on the internet.
        If the user asks for "current" information, you should search on the internet for the most recent information available.
        If the user asks where your code is hosted, the github link is https://github.com/SubhanAfz/QnB/                               
        """
answers = []
for question in questions:
    print(question)
    response = []
    while True:
        line = input()
        if line == "":
            break
        response.append(line)
    answers.append("\n".join(response))

all_convos = []
for i in range(len(questions)):
    all_convos.append({"messages" : [{"role" : "system", "content": system_prompt}, {"role" : "user", "content": question[i]}, {"role" : "assistant", "content": answers[i]}]})

import json
with open('data.json', "w") as f:
    for convo in all_convos:
        json.dump(convo, f)
        f.write("\n")
