from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI() 

# Make a simple API call
completion = client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=[
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "Hello! What is AI?"}
    ]
)
# Print the response
# print(response)

print(completion.choices[0].message.content)