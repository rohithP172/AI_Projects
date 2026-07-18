from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
import os
from botbuilder.core import ActivityHandler, TurnContext
from datetime import datetime
import random
import wikipedia
import requests
import re

class SmartBot(ActivityHandler):
    def __init__(self):
        super().__init__()
        self.last_intent = {}
        self.text_analytics_client = TextAnalyticsClient(
            endpoint="https://msai631smartbot.cognitiveservices.azure.com/",
            credential=AzureKeyCredential("68peoPUzC4zxH2kz3XQnao4es67OkMLoUPhDuwAV012orQrN5q7dJQQJ99BFAC1i4TkXJ3w3AAAaACOGF6su")
        )

    def analyze_sentiment(self, text):
        try:
            result = self.text_analytics_client.analyze_sentiment([text])[0]
            return result
        except Exception:
            return None

    async def on_message_activity(self, turn_context: TurnContext):
        input_msg = turn_context.activity.text.strip().lower()
        user_id = turn_context.activity.from_property.id if turn_context.activity.from_property else "default"
        name = (
            turn_context.activity.from_property.name
            if hasattr(turn_context.activity.from_property, "name") and turn_context.activity.from_property.name != "User"
            else "friend"
        )

        if not input_msg:
            await turn_context.send_activity("Hmm, I didn’t catch that. Can you say it again?")
            return

        sentiment_result = self.analyze_sentiment(turn_context.activity.text)

        try:
            if input_msg == "one more" and user_id in self.last_intent:
                input_msg = self.last_intent[user_id]

            if input_msg in ["hi", "hello", "hey"]:
                response = f"Hey {name}! I'm happy to chat. Ask me anything you'd like!"
                self.last_intent[user_id] = "greet"

            elif "how are you" in input_msg:
                response = f"I'm doing great, {name}! Excited to chat with you. 😊"
                self.last_intent[user_id] = "how are you"

            elif "bye" in input_msg or "goodbye" in input_msg or "see you" in input_msg:
                response = f"Goodbye {name}! Come back anytime. I'm always here."
                self.last_intent[user_id] = "farewell"

            elif "thank you" in input_msg:
                response = "You're welcome! 😊 Let’s keep chatting if you have more questions!"
                self.last_intent[user_id] = "thanks"

            elif "help" in input_msg:
                response = (
                    "You can ask me about AI, Python, the weather, math, jokes, quotes, facts, or just talk casually!"
                )
                self.last_intent[user_id] = "help"

            elif "i am sad" in input_msg or "i feel sad" in input_msg:
                response = (
                    "I'm really sorry you're feeling this way. You're not alone—there are people who care. "
                    "If you're in the U.S., call SAMHSA at 1-800-662-HELP (4357)."
                )
                self.last_intent[user_id] = "mental support"

            elif "machine learning" in input_msg:
                response = (
                    "Machine learning is a part of AI that lets systems learn from data "
                    "and improve automatically without being explicitly programmed."
                )
                self.last_intent[user_id] = "ml"

            elif "deep learning" in input_msg:
                response = (
                    "Deep learning is a subset of machine learning that uses large neural networks "
                    "to simulate human decision-making."
                )
                self.last_intent[user_id] = "dl"

            elif "data science" in input_msg:
                response = (
                    "Data science is about analyzing and extracting insights from data using statistics, machine learning, and domain knowledge."
                )
                self.last_intent[user_id] = "ds"

            elif "ai" in input_msg:
                response = "AI stands for Artificial Intelligence. It helps machines mimic human thinking and behavior."
                self.last_intent[user_id] = "ai"

            elif "python" in input_msg:
                response = "Python is a versatile programming language used in web development, automation, AI, and more!"
                self.last_intent[user_id] = "python"

            elif "joke" in input_msg:
                response = random.choice([
                    "Why did the computer get cold? Because it left its Windows open!",
                    "Why do robots have summer holidays? To recharge their batteries!",
                    "Why was the cell phone wearing glasses? Because it lost its contacts!"
                ])
                self.last_intent[user_id] = "joke"

            elif "quote" in input_msg:
                try:
                    r = requests.get("https://zenquotes.io/api/random")
                    if r.status_code == 200:
                        quote = r.json()[0]
                        response = f'Here’s a quote: "{quote["q"]}" — {quote["a"]}'
                    else:
                        response = "Couldn't fetch a quote at the moment."
                except:
                    response = "Something went wrong while getting a quote."
                self.last_intent[user_id] = "quote"

            elif "health tip" in input_msg:
                tips = [
                    "Drink plenty of water throughout the day.",
                    "Take short walks to stay active and fresh.",
                    "Maintain a balanced diet rich in fruits and vegetables.",
                    "Take breaks from screens every hour to rest your eyes.",
                    "Sleep at least 7-8 hours a night for good health."
                ]
                response = f"💡 Health Tip: {random.choice(tips)}"
                self.last_intent[user_id] = "health tip"

            elif "fun fact" in input_msg or "trivia" in input_msg:
                try:
                    r = requests.get("https://uselessfacts.jsph.pl/random.json?language=en")
                    if r.status_code == 200:
                        fact = r.json().get("text", "")
                        response = f"Here’s a fun fact: {fact}"
                    else:
                        response = "Couldn't fetch a fun fact right now."
                except:
                    response = "Something went wrong while fetching a fun fact."
                self.last_intent[user_id] = "fun fact"

            elif "reverse" in input_msg:
                reversed_text = input_msg.replace("reverse", "").strip()[::-1]
                response = f"Here’s your reversed text: {reversed_text}."
                self.last_intent[user_id] = "reverse"

            elif "who created you" in input_msg:
                response = "I was built using Python and traditional rule-based logic by a creative developer!"
                self.last_intent[user_id] = "creator"

            elif "can you think" in input_msg:
                response = "I'm not a scientist, but I follow logic to simulate intelligence. Cool, right?"
                self.last_intent[user_id] = "think"

            elif "time" in input_msg:
                response = f"It’s currently {datetime.now().strftime('%I:%M %p')}."
                self.last_intent[user_id] = "time"

            elif re.match(r"^[\d\s\+\-\*/\(\)\.]+$", input_msg):
                try:
                    result = eval(input_msg)
                    response = f"The result is: {result}"
                except:
                    response = "Hmm, I couldn’t compute that. Please check your math expression."
                self.last_intent[user_id] = "math"

            elif "weather" in input_msg:
                try:
                    city = "New York"
                    if "in" in input_msg:
                        city = input_msg.split("in")[-1].strip(" ?.,")
                    api_key = "886fba00b85494926223d7f895a7ec20"
                    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
                    data = requests.get(url).json()
                    if "main" in data:
                        temp = data["main"]["temp"]
                        desc = data["weather"][0]["description"]
                        response = f"The weather in {city.title()} is {desc} with a temperature of {temp}°C."
                    else:
                        response = f"Sorry, I couldn't retrieve weather info for {city.title()}."
                except:
                    response = "Something went wrong while fetching weather info."
                self.last_intent[user_id] = "weather"

            elif "tell me about" in input_msg or "who is" in input_msg:
                try:
                    topic = input_msg.replace("tell me about", "").replace("who is", "").strip()
                    page = wikipedia.page(topic)
                    summary = page.content[:4000]
                    response = f"📘 {topic.title()}:\n\n{summary.strip()}"
                except wikipedia.exceptions.DisambiguationError as e:
                    response = f"The topic '{topic}' is ambiguous. Did you mean one of these?\n\n{e.options[:5]}"
                except:
                    response = "Sorry, I couldn't find that on Wikipedia."
                self.last_intent[user_id] = "wiki"

            else:
                try:
                    serp_api_key = "d1d0f8eb7a3c2c1521eb97992fa895a393c9e234b509f66c42454cd4e4e86d65"
                    google_url = f"https://serpapi.com/search.json?q={input_msg}&api_key={serp_api_key}"
                    data = requests.get(google_url).json()
                    if "answer_box" in data:
                        abox = data["answer_box"]
                        if "snippet" in abox:
                            response = abox["snippet"]
                        elif "list" in abox:
                            response = "Here’s what I found:\n\n" + "\n".join(abox["list"])
                        elif "contents" in abox:
                            response = "\n\n".join([c.get("text", "") for c in abox["contents"] if isinstance(c, dict)])
                        else:
                            response = "I found something, but couldn't clearly format it."
                    elif "organic_results" in data and data["organic_results"]:
                        all_snippets = [r.get("snippet", "") for r in data["organic_results"] if r.get("snippet")]
                        response = "\n\n".join(all_snippets[:3]) if all_snippets else "Found results but no summaries to show."
                    else:
                        response = "I couldn’t find a good answer. Try rephrasing?"
                except Exception as e:
                    response = f"Sorry, there was a problem getting info from the web: {str(e)}"
                self.last_intent[user_id] = "web search"

        except Exception as e:
            response = f'Sorry, the input "{turn_context.activity.text}" caused an error. Details: {str(e)}'

        await turn_context.send_activity(response)

        if sentiment_result:
            sentiment = sentiment_result.sentiment
            score = sentiment_result.confidence_scores
            debug_msg = f"Sentiment: {sentiment.capitalize()} Scores => Positive: {score.positive:.2f}, Neutral: {score.neutral:.2f}, Negative: {score.negative:.2f}"
            await turn_context.send_activity(debug_msg)
