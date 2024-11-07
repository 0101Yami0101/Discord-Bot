import discord
from discord.ext import commands
from discord import app_commands
import random
import string
import asyncio

class Quiz(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.active_quizzes = {'NWEG1Z': {'name': '🍌 Banene 🍌', 'description': 'A fun fruit quiz!', 'timer': 10, 'questions': [{'question': 'What color are bananas?', 'options': ['Red', 'Green', 'Yellow', 'Blue'], 'correct_answer': 3}, {'question': 'Do bananas float?', 'options': ['Yes', 'No'], 'correct_answer': 1}]}}
        self.quiz_group = app_commands.Group(name="quiz", description="📚 Manage quizzes.")
        self.quiz_group.command(name="create", description="Start creating a new quiz.")(self.create_quiz)
        self.quiz_group.command(name="start", description="Start a quiz in the channel by quiz ID.")(self.start_quiz)
        self.quiz_group.command(name="view", description="View details of an existing quiz.")(self.view_quiz)
        bot.tree.add_command(self.quiz_group)

    async def create_quiz(self, interaction: discord.Interaction):
        await interaction.response.send_message("I'll guide you through the quiz setup in your DMs 📩", ephemeral=True)
        await interaction.user.send("🚀 Let's start creating your quiz!")

        quiz = {}

        quiz['name'] = await self.prompt_dm(interaction, "What would you like to name the quiz? 🎨")
        if not quiz['name']:
            await interaction.user.send("❌ Quiz creation canceled. No name was provided.")
            return

        quiz['description'] = await self.prompt_dm(interaction, "Provide a brief description of the quiz (or type 'skip' to leave it blank). ✏️")
        if quiz['description'].lower() == 'skip':
            quiz['description'] = "No description provided."

        timer_response = await self.prompt_dm(interaction, "⏱️ Set a timer (in seconds) for each question response (default is 30 seconds):")
        quiz['timer'] = int(timer_response) if timer_response.isdigit() else 30


        quiz['questions'] = []
        await interaction.user.send("📝 Now, let's add questions to your quiz. Type 'done' when finished adding questions or 'view' to see the current questions.")

        question_count = 0
        while True:
            question_text = await self.prompt_dm(interaction, f"Enter the question text for question #{question_count + 1} 🧐 (or type 'done' to finish, 'view' to see questions):")
            if question_text.lower() == 'done':
                break
            elif question_text.lower() == 'view':
                if quiz['questions']:
                    question_list = "\n".join(f"Q{i + 1}: {q['question']}" for i, q in enumerate(quiz['questions']))
                    await interaction.user.send(f"Currently added questions:\n{question_list}")
                else:
                    await interaction.user.send("No questions have been added yet.")
                continue
            if question_text:
                question_count += 1
                options = []
                option_limit = 4  # Default option limit

                for i in range(option_limit):
                    option_text = await self.prompt_dm(interaction, f"Enter option {i + 1} for question #{question_count} 📝 (or type 'skip' to end options):")
                    if option_text.lower() == 'skip':
                        break
                    options.append(option_text)

            
                option_display = "\n".join(f"{i + 1}. {opt}" for i, opt in enumerate(options))
                await interaction.user.send(f"Options for question #{question_count}:\n{option_display}")
                correct_answer = await self.prompt_dm(interaction, f"Which option number is the correct answer? (1-{len(options)}) ✅")

                # Add the question
                quiz['questions'].append({
                    "question": question_text,
                    "options": options,
                    "correct_answer": int(correct_answer)
                })

        #Unique quiz ID
        quiz_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        self.active_quizzes[quiz_id] = quiz
        await interaction.user.send(f"✅ Quiz creation complete! Your quiz ID is `{quiz_id}`. Use `/quiz start {quiz_id}` in a server channel to start it.")

    async def start_quiz(self, interaction: discord.Interaction, quiz_id: str):
        quiz = self.active_quizzes.get(quiz_id)
        if not quiz:
            await interaction.response.send_message(f"❌ Quiz ID `{quiz_id}` not found. Please check the ID and try again.", ephemeral=True)
            return

        await interaction.response.send_message(f"🎉 Starting the quiz: **{quiz['name']}**!", ephemeral=True)
        channel = interaction.channel
        scores = {}
        streaks = {}  # To track consecutive correct answers
        base_points = 1  # Base points for correct answer

        for question in quiz['questions']:

            #delay before every next question except first
            if quiz['questions'].index(question) != 0:
                await asyncio.sleep(quiz['timer'])
            
            emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣']
            options_text = "\n".join(f"{emojis[i]} {option}" for i, option in enumerate(question['options']))
            embed = discord.Embed(title=question['question'], description=options_text, color=discord.Color.blue())
            question_msg = await channel.send(embed=embed)

            for emoji in emojis[:len(question['options'])]:
                await question_msg.add_reaction(emoji)

            
            reacted_users = set()#Store users who already reacted

            def check_reaction(reaction, user):
                return user != self.bot.user and str(reaction.emoji) in emojis and reaction.message.id == question_msg.id

            try:
                while True:
                    reaction, responder = await asyncio.wait_for(
                        self.bot.wait_for('reaction_add', check=check_reaction),
                        timeout=quiz['timer']
                    )

                    if responder in reacted_users:
                        await reaction.remove(responder)
                        continue

                    reacted_users.add(responder)

                    selected_option = emojis.index(str(reaction.emoji)) + 1
                    if selected_option == question['correct_answer']:
                        scores[responder] = scores.get(responder, 0) + base_points
                        streaks[responder] = streaks.get(responder, 0) + 1
                        if streaks[responder] >= 3:  # +2 for 3 consecutive correct answers
                            scores[responder] += 2 
                    else: #deduct for incorrect answer
                        scores[responder] = scores.get(responder, 0) - 1
                        streaks[responder] = 0  

            except asyncio.TimeoutError:
                await channel.send("⏰ Time's up for this question!")

            

        #FInal scores and embed
        leaderboard = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        embed = discord.Embed(title="🏅 Quiz Over!", description="Here are the final scores:", color=discord.Color.gold())
        for user, score in leaderboard:
            embed.add_field(name=user.display_name, value=f"Score: {score} 🏅", inline=False)

        for idx, question in enumerate(quiz['questions'], start=1):
            correct_option = question['options'][question['correct_answer'] - 1]
            embed.add_field(name=f"Q{idx}: {question['question']}", value=f"Correct Answer: {correct_option} ✅", inline=False)

        await channel.send(embed=embed)

    async def view_quiz(self, interaction: discord.Interaction, quiz_id: str):
        quiz = self.active_quizzes.get(quiz_id)
        if not quiz:
            await interaction.response.send_message(f"❌ Quiz ID `{quiz_id}` not found. Please check the ID and try again.", ephemeral=True)
            return

        quiz_details = f"**Name:** {quiz['name']} 🎓\n**Description:** {quiz['description']}\n"
        for idx, question in enumerate(quiz['questions'], start=1):
            options = "\n".join(f"{i + 1}. {option}" for i, option in enumerate(question["options"]))
            quiz_details += f"\n**Q{idx}:** {question['question']}\n{options}\n**Correct Answer:** Option {question['correct_answer']} ✅"

        await interaction.user.send(quiz_details)

    async def prompt_dm(self, interaction: discord.Interaction, prompt_message: str):
        await interaction.user.send(prompt_message)

        def check(m):
            return m.author == interaction.user and isinstance(m.channel, discord.DMChannel)

        try:
            msg = await self.bot.wait_for('message', check=check, timeout=60)
            return msg.content
        except asyncio.TimeoutError:
            await interaction.user.send("⏰ Timed out. You took too long to respond.")
            return None

async def setup(bot: commands.Bot):
    await bot.add_cog(Quiz(bot))
