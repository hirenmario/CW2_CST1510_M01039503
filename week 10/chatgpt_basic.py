from openai import OpenAI

# Initialize the OpenAI client with your API key
client = OpenAI(api_key='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')
# Make a simple API call
completion = client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=[
     {"role": "system", "content": "You are a helpful assistant."},
     {"role": "user", "content": "Hello! What is AI?"}
]
)
# Print the response

print(completion.choices[0].message.content)