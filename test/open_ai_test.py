from openai import OpenAI
import os
import json

from dotenv import load_dotenv

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

def generate_prompt(data):
    chat_input = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"Create a detailed description for an image generation prompt based on the following hero details. Do not use the word 'character', use 'hero' instead: {json.dumps(data)}"}
    ]

    try:
        chat_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=chat_input
        )
        detailed_prompt = chat_response.choices[0].message.content
        #print(detailed_prompt)
        return detailed_prompt
    except Exception as e:
        print(f"Error generating detailed prompt: {e}")
        return None

def generate_image(prompt):
    try:
        response = client.images.generate(model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        n=1)
        image_url = response.data[0].url
        return image_url
    except Exception as e:
        print(f"Error generating image: {e}")
        return None

# Example character data
character_data = {
    "name": "Shadow",
    "race": "Elf",
    "class": "Thief",
    "age": "120",
    "description": "A nimble and cunning elf with a talent for stealth.",
    "appearance": "Slender build, sharp eyes, always dressed in dark clothing.",
    "traits": "Quick, Agile, Intelligent",
    "background": "Grew up in the dark alleys of the city, learning to pickpocket and sneak.",
    "history": "Shadow has a history of heists and infiltration missions, always managing to slip away unnoticed."
}

# Generate detailed prompt
prompt = generate_prompt(character_data)
if prompt:
    print(f"Generated prompt: {prompt}")

    # Generate image
    image_url = generate_image(prompt)
    if image_url:
        print(f"Generated image URL: {image_url}")
