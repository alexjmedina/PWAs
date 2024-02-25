from openai import OpenAI

client = OpenAI()

completion = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ]
)

# Assuming 'choices' is the correct attribute based on the structure you've indicated
# and 'message' contains the response text.
# The correct attribute names and structure depend on the specific version of the OpenAI Python client you're using.
print(completion.choices[0].message)

