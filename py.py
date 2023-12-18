import requests
import tkinter as tk
import configparser

from tkinter import scrolledtext, messagebox
from tkinter.font import Font

#Load config
config = configparser.ConfigParser()
config.read('/home/cam/Desktop/gpt-agents/config.ini')
api_key1 = config.get('API_KEYS', 'api_key1')
api_key2 = config.get('API_KEYS', 'api_key2')

def truncate_conversation_history(conversation_history, max_tokens=2300):
    total_tokens = 0
    truncated_history = []

    for message in reversed(conversation_history):
        total_tokens += len(message['content'].split())
        if total_tokens > max_tokens:
            break
        truncated_history.append(message)

    return list(reversed(truncated_history))

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
        'model': 'gpt-4-0613',
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

def main():
    api_key = api_key1
    conversation_history = []
    root = tk.Tk()
    root.configure(bg='black')

    my_font = Font(family="Consolas", size=13)

    prompt_entry = tk.Text(root, height=10, bg='black', fg='white', font=my_font)
    prompt_entry.grid(row=0, column=0, columnspan=2, sticky=tk.N+tk.S+tk.E+tk.W)

    def chat():
        prompt = prompt_entry.get('1.0', tk.END).strip()
        prompt_entry.delete('1.0', tk.END)
        truncated_history = truncate_conversation_history(conversation_history)
        try:
            response = chat_gpt(api_key, prompt, truncated_history)
            conversation_history.extend([
                {'role': 'user', 'content': prompt},
                {'role': 'assistant', 'content': response}
            ])
            output_area.insert(tk.END, "\nUser: " + prompt)
            output_area.insert(tk.END, "\nChatGPT: " + response)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def copy_output():
        root.clipboard_clear()
        root.clipboard_append(output_area.get('1.0', tk.END))

    chat_button = tk.Button(root, text="Chat", command=chat, bg='black', fg='white', font=my_font, width=10, height=3)
    chat_button.grid(row=1, column=0, sticky=tk.N+tk.S+tk.E+tk.W)

    copy_button = tk.Button(root, text="Copy Output", command=copy_output, bg='black', fg='white', font=my_font, width=10, height=3)
    copy_button.grid(row=1, column=1, sticky=tk.N+tk.S+tk.E+tk.W)

    output_area = scrolledtext.ScrolledText(root, bg='black', fg='white', font=my_font)
    output_area.grid(row=2, column=0, columnspan=2, sticky=tk.N+tk.S+tk.E+tk.W)

    root.grid_rowconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=1)
    root.grid_rowconfigure(2, weight=1)
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)

    root.mainloop()

if __name__ == "__main__":
    main()