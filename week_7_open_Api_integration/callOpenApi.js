async function hook(event: IO.IncomingEvent, context: LLMZ.CreateContext): Promise<void> {

const axios = require('axios');

/** Use the incoming message as prompt */
const prompt = event.preview || event.payload;

try {
  const response = await axios.post(
    'https://api.openai.com/v1/chat/completions',
    {
      model: 'gpt-3.5-turbo', 
      messages: [{ role: 'user', content: prompt }]
    },
    {
      headers: {
// replace open api key with the user credentials.
        Authorization: 'Bearer "ENTER-OPEN-API-KEY"',
        'Content-Type': 'application/json'
      }
    }
  );

  const reply = response.data.choices[0].message.content;

  
  event.payload = reply;

} catch (error) {
  console.error("OpenAI API error:", error.message);
  event.payload = "Sorry, I couldn’t reach the AI service.";
}


}
