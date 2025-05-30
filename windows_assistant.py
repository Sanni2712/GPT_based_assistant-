import tkinter as tk
import subprocess
import os
import json
from openai import OpenAI
import getpass

user = getpass.getuser()
print("username detected:")
print(user)


client = OpenAI(api_key="your_api_key_here")

# === GPT COMMUNICATION ===
def send_to_gpt(user_input):
    messages = [
        {
        "role": "system",
        "content": (
            "You are a system assistant. Do not explain things. Do not give instructions. "
            "Only respond in JSON. Use the following keys: "
            "'bash' for shell commands to execute, "
            "'display' for showing text in the UI, "
            "'request' to ask the app for more information (e.g. list of files). "
            "If a user says 'Open Desktop folder' or any other folder like pictures or screenshots, respond with any appropriate address: "
            "{ \"bash\": \"explorer C:\\\\Users\\\\{user}\\\\<folder>\" }"
        )
    },

        {"role": "user", "content": user_input}
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",  # or gpt-4.0-turbo / gpt-4.1-mini
            messages=messages
        )
        content = response.choices[0].message.content.strip()

        # Try to parse JSON safely
        if not content.startswith("{"):
            return {"display": f"GPT returned non-JSON response:\n{content}"}
        return json.loads(content)

    except json.JSONDecodeError:
        return {"display": "Error: GPT response was not valid JSON."}
    except Exception as e:
        return {"display": f"Error from GPT: {str(e)}"}

# === SYSTEM HELPERS ===
def fulfill_request(request_type, path="."):
    try:
        if request_type == "list_files":
            return os.listdir(path)
        elif request_type == "read_file":
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
    except Exception as e:
        return f"Request error: {e}"

# === EXECUTION HANDLER ===
def handle_response(resp):
    if 'display' in resp:
        display_text(resp['display'])
    if 'bash' in resp:
        try:
            subprocess.Popen(resp['bash'], shell=True)
        except Exception as e:
            display_text(f"Command error: {e}")
    if 'request' in resp:
        req = resp['request']
        path = resp.get("path", ".")
        result = fulfill_request(req, path)
        follow_up = send_to_gpt(f"Result of {req} for {path}:\n{result}")
        handle_response(follow_up)

# === GUI FUNCTIONS ===
def display_text(text):
    output_box.config(state="normal")
    output_box.insert(tk.END, text + "\n\n")
    output_box.config(state="disabled")
    output_box.see(tk.END)

def on_enter(event=None):
    user_input = input_field.get()
    input_field.delete(0, tk.END)
    response = send_to_gpt(user_input)
    handle_response(response)

# === TKINTER SETUP ===
app = tk.Tk()
app.title("Test Assistant 1.0")
app.geometry("600x400")

input_field = tk.Entry(app, width=80)
input_field.pack(pady=10)
input_field.bind("<Return>", on_enter)

output_box = tk.Text(app, height=20, state="disabled", wrap="word")
output_box.pack(padx=10, pady=10)

# Start the assistant
display_text("Welcome to Test Assistant 1.0!")
app.mainloop()

#
