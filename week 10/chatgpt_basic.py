from openai import OpenAI

# Initialize the OpenAI client with your API key
client = OpenAI(api_key='YOUR_API_KEY_HERE')
# Make a simple API call
completion = client.chat.completions.create(
model="gpt-4o",
messages=[
{"role": "system", "content": "You are a helpful assistant."},
{"role": "user", "content": "Hello! What is AI?"}])
# Print the response

print(completion.choices[0].message.content)