import discord
import requests
import configparser
import os

# Set the possible base directories for config.ini
base_directories = [
    r'C:\Users\Cameron\Desktop\gpt-agents',
    '/home/cam/Desktop/gpt-agents'
]

# Attempt to read the configuration file from each base directory
config = configparser.ConfigParser()

for base_directory in base_directories:
    config_file_path = os.path.join(base_directory, 'config.ini')

    try:
        config.read(config_file_path)
        # If successful, break out of the loop
        break
    except FileNotFoundError:
        # If the file is not found, try the next base directory
        continue
    except configparser.Error as e:
        print(f"Error reading {config_file_path}: {e}")
        break

# Use the API keys as needed in your script
api_key1 = config.get('API_KEYS', 'api_key1')
api_key3 = config.get('API_KEYS', 'api_key3')  # Discord token

def chat_gpt(api_key, prompt, conversation_history=None):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    messages = [{'role': 'system', 'content': 'I want you to act like a Python interpreter. I will give you Python code, and you will execute it. Please provide easy to understand explanations and then after determining the issue, offer full code solutions shown, with clear instructions below regarding the bits of code that need to be removed and changes.'}]

    if conversation_history:
        messages.extend(conversation_history)

    messages.append({'role': 'user', 'content': prompt})

    data = {
        'model': 'gpt-4-1106-preview',
        'messages': messages,
        'temperature': 0.5,
        'top_p': 1,
        'max_tokens': 2560
    }
    response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)

    if response.status_code == 200:
        result = response.json()
        message = result['choices'][0]['message']['content']
        return message.strip()
    else:
        raise Exception(f"API request failed with status code {response.status_code}. Error details: {response.text}")

def chat_cybersecurity(api_key, prompt, conversation_history=None):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    messages = [{'role': 'system', 'content': 'I want you to act like a Cybersecurity expert. I will ask questions about network systems and command line scripting as I am a novice learning. Please provide easy to understand explanations and then after determining the issue, offer clear instructions.'}]

    if conversation_history:
        messages.extend(conversation_history)

    messages.append({'role': 'user', 'content': prompt})

    data = {
        'model': 'gpt-4-1106-preview',
        'messages': messages,
        'temperature': 0.5,
        'top_p': 1,
        'max_tokens': 2560
    }
    response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)

    if response.status_code == 200:
        result = response.json()
        message = result['choices'][0]['message']['content']
        return message.strip()
    else:
        raise Exception(f"API request failed with status code {response.status_code}. Error details: {response.text}")

# Command Handlers
command_handlers = {
    '/p': chat_gpt,
    '/c': chat_cybersecurity,
    # Add more commands and handlers as needed
}

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return

        # respond only to DMs
        if not isinstance(message.channel, discord.channel.DMChannel):
            return

        # process the command
        for prefix, handler in command_handlers.items():
            if message.content.startswith(prefix):
                command = message.content[len(prefix):].strip()
                response = handler(api_key1, command)
                break
        else:
            return  # Ignore messages that don't match any command prefix

        # Check if the response is too long
        if len(response) > 2000:
            # If it's too long, split it into chunks of 2000 characters
            chunks = [response[i:i + 2000] for i in range(0, len(response), 2000)]
            for chunk in chunks:
                await message.channel.send(chunk)
        else:
            await message.channel.send(response)

intents = discord.Intents.default()
intents.messages = True

client = MyClient(intents=intents)
client.run(api_key3)
