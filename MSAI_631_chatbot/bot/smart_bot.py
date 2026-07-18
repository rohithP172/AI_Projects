from botbuilder.core import ActivityHandler, TurnContext
from datetime import datetime
import random
import wikipedia
import requests

class SmartBot(ActivityHandler):
    async def on_message_activity(self, turn_context: TurnContext):
        input_msg = turn_context.activity.text.strip().lower()
        name = (
            turn_context.activity.from_property.name
            if hasattr(turn_context.activity.from_property, "name") and turn_context.activity.from_property.name != "User"
            else "friend"
        )

        if not input_msg:
            await turn_context.send_activity("Hmm, I didn’t catch that. Can you say it again?")
            return

        try:
            
            if "machine learning" in input_msg:
                response = (
                    "Machine learning is a part of AI that lets systems learn from data "
                    "and improve automatically without being explicitly programmed."
                )

            elif "deep learning" in input_msg:
                response = (
                    "Deep learning is a subset of machine learning that uses large neural networks "
                    "to simulate human decision-making."
                )

            elif "data science" in input_msg:
                response = (
                    "Data science is about analyzing and extracting insights from data using statistics, machine learning, and domain knowledge."
                )

            elif any(word in input_msg for word in ["hi", "hello", "hey"]):
                response = f"Hey {name}! I'm happy to chat. Ask me anything you'd like!"

            elif "how are you" in input_msg:
                response = f"I'm doing great, {name}! Excited to chat with you. 😊"

            elif "time" in input_msg:
                response = f"It’s currently {datetime.now().strftime('%I:%M %p')}."

            elif "ai" in input_msg:
                response = "AI stands for Artificial Intelligence. It helps machines mimic human thinking and behavior."

            elif "python" in input_msg:
                response = (
                    "Python is a versatile programming language used in web development, automation, AI, and more!"
                )

            elif "joke" in input_msg:
                response = random.choice([
                    "Why did the computer get cold? Because it left its Windows open!",
                    "Why do robots have summer holidays? To recharge their batteries!",
                    "Why was the cell phone wearing glasses? Because it lost its contacts!"
                ])

            elif "reverse" in input_msg:
                reversed_text = input_msg.replace("reverse", "").strip()[::-1]
                response = f"Here’s your reversed text: {reversed_text}."

            elif "who created you" in input_msg:
                response = "I was built using Python and traditional rule-based logic by a creative developer!"

            elif "can you think" in input_msg:
                response = "I'm not scientist , but I follow logic to simulate intelligence. Cool, right?"

            elif any(word in input_msg for word in ["bye", "goodbye", "see you"]):
                response = f"Goodbye {name}! Come back anytime. I'm always here."

            elif "thank you" in input_msg:
                response = "You're welcome! 😊 Let’s keep chatting if you have more questions!"

            elif "help" in input_msg:
                response = (
                    "You can ask me about AI, Python, the weather, jokes, machine learning, or just talk casually!"
                )

            elif "weather" in input_msg:
                city = "New York"
                if "in" in input_msg:
                    city = input_msg.split("in")[-1].strip()
                api_key = "886fba00b85494926223d7f895a7ec20"  
                url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
                data = requests.get(url).json()
                if "main" in data:
                    temp = data["main"]["temp"]
                    desc = data["weather"][0]["description"]
                    response = f"The weather in {city.title()} is {desc} with a temperature of {temp}°C."
                else:
                    response = f"Sorry, I couldn't retrieve weather info for {city.title()}."

            elif "tell me about" in user_input or "who is" in user_input:
                try:
                    topic = user_input.replace("tell me about", "").replace("who is", "").strip()
                    summary = wikipedia.summary(topic, sentences=2)
                    response = f"Here’s what I found about {topic.title()}: {summary}"
                except:
                    response = "I couldn't find that on Wikipedia. Want me to try a web search?"

            else:
                
                serp_api_key = "d1d0f8eb7a3c2c1521eb97992fa895a393c9e234b509f66c42454cd4e4e86d65"
                query = user_input
                google_url = f"https://serpapi.com/search.json?q={query}&api_key={serp_api_key}"
                google_data = requests.get(google_url).json()
                if "answer_box" in google_data and "snippet" in google_data["answer_box"]:
                    response = google_data["answer_box"]["snippet"]
                elif "organic_results" in google_data and google_data["organic_results"]:
                    response = google_data["organic_results"][0].get("snippet", "I found something, but couldn’t extract the details.")
                else:
                    response = (
                        f"Hmm, I couldn't find a good answer for that, {name}. Try rephrasing it or asking me something else!"
                    )

        except Exception as e:
            response = f'Sorry, the input "{turn_context.activity.text}" caused an error. Details: {str(e)}'

        await turn_context.send_activity(response)
