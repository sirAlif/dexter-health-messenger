import asyncio
import websockets
import httpx
import json
from config.conf import Config
import threading
import sys

# Load environment variables
conf = Config()


async def sign_up():
    try:
        username = input("Username: ")
        password = input("Password: ")
        async with httpx.AsyncClient() as client:
            response = await client.post(f"http://{conf.API_HOST}:{conf.API_PORT}/auth/signup/",
                                         json={"username": username, "password": password})
        if response.status_code == 200:
            print(response.json().get("message", "Sign-up successful"))
            token = response.json().get("access_token")
            return response.json().get("user_id"), token
        else:
            print(f"Error: {response.json().get('detail', 'Failed to sign up')}")
            return None
    except Exception as e:
        print(f"Sign-up failed: {e}")
        return None


async def log_in():
    try:
        username = input("Username: ")
        password = input("Password: ")
        async with httpx.AsyncClient() as client:
            response = await client.post(f"http://{conf.API_HOST}:{conf.API_PORT}/auth/login/",
                                         json={"username": username, "password": password})
        if response.status_code == 200:
            print("Login successful!")
            token = response.json().get("access_token")
            return response.json().get("user_id"), token
        else:
            print(f"Error: {response.json().get('detail', 'Invalid credentials')}")
            return None
    except Exception as e:
        print(f"Login failed: {e}")
        return None


async def chat(user_id, token, contact_username, new_chat):
    ws_url = f"ws://{conf.API_HOST}:{conf.API_PORT}/chat/ws/{user_id}?token={token}"

    try:
        # Fetch chat history before starting the WebSocket connection
        async with httpx.AsyncClient() as client:
            history_response = await client.get(
                f"http://{conf.API_HOST}:{conf.API_PORT}/chat/history/{user_id}?contact={contact_username}",
                headers={"Authorization": f"Bearer {token}"}
            )
            if history_response.status_code == 200:
                if not new_chat:
                    history = history_response.json()
                    print(f"\033[1m\nChat History with {contact_username}:\033[0m")
                    for message in history:
                        if message['sender_id'] == user_id:
                            print(f"You: {message['content']}")
                        else:
                            print(f"{contact_username}: {message['content']}")
            elif 400 <= history_response.status_code < 500:
                error_detail = history_response.json().get("detail", "No detail provided")
                print(f"Error: {error_detail}")
                return
            else:
                print(f"Failed to fetch chat history with {contact_username}.")

        # Now proceed with WebSocket connection
        async with websockets.connect(ws_url) as ws:
            print(f"\nConnected to chat with {contact_username}. Type 'exit' to quit.")

            # Shared variable to stop threads
            stop_event = threading.Event()

            # Function to read user input in a separate thread
            def read_input(loop):
                while not stop_event.is_set():
                    msg = input(f"You: ")
                    if msg.lower() == "exit":
                        stop_event.set()
                        loop.call_soon_threadsafe(asyncio.create_task, ws.close())
                        break
                    if len(msg) == 0:
                        print("Message cannot be empty.")
                        continue
                    loop.call_soon_threadsafe(asyncio.create_task, ws.send(json.dumps({
                        "contact": contact_username,
                        "sender_id": user_id,
                        "content": msg
                    })))

            # Get the current event loop
            loop = asyncio.get_event_loop()

            # Start input reader in a separate thread
            input_thread = threading.Thread(target=read_input, args=(loop,), daemon=True)
            input_thread.start()

            # Coroutine to receive messages
            async def receive_messages():
                while not stop_event.is_set():
                    try:
                        incoming_message = await ws.recv()
                        message_json = json.loads(incoming_message)
                        if message_json["sender"] == contact_username:
                            content = message_json['content']
                            sys.stdout.write("\r" + " " * 100)  # Clear the line
                            sys.stdout.flush()
                            print(f"\r{contact_username}: {content}")
                            sys.stdout.write("You: ")
                            sys.stdout.flush()
                    except websockets.ConnectionClosed:
                        print("Connection closed.")
                        break
                    except Exception as exception:
                        print(f"Error receiving message: {exception}")
                        break

            # Run the receiving coroutine
            try:
                await receive_messages()
            except asyncio.CancelledError:
                pass
            finally:
                stop_event.set()
                input_thread.join()

    except websockets.InvalidHandshake:
        print("Error: Failed to establish connection. Invalid user.")
    except Exception as e:
        print(f"Failed to connect to chat: {e}")


async def get_previous_contacts(user_id: int, token):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://{conf.API_HOST}:{conf.API_PORT}/chat/contacts/{user_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code == 200:
                contacts = response.json()
                return contacts
            else:
                print("Failed to fetch previous chats.")
                return []
    except Exception as e:
        print(f"Error fetching previous chats: {e}")
        return []


async def chat_with_ai(user_id: int, token: str):
    print("\nConnected to the AI chat. Type 'exit' to quit.\n")
    while True:
        prompt = input("You: ")
        if prompt.lower() == "exit":
            print("\nExiting AI chat.\n")
            break
        if len(prompt.strip()) == 0:
            print("Message cannot be empty.")
            continue
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(10)) as client:
                response = await client.post(
                    f"http://{conf.API_HOST}:{conf.API_PORT}/ai/chat/{user_id}",
                    json={"prompt": prompt},
                    headers={"Authorization": f"Bearer {token}"}
                )
            if response.status_code == 200:
                print(f"AI: {response.json()['response']}")
            else:
                print(f"Error: {response.json().get('detail', 'Failed to chat with AI')}")
        except Exception as e:
            print(f"Failed to connect to AI: {e}")


async def main():
    while True:
        try:
            user_id = -1
            token = ""
            print("\n1. Sign Up\n2. Log In\n3. Exit")
            choice = input("Select: ")
            if not choice.isdigit() or int(choice) not in [1, 2, 3]:
                print("Invalid selection. Please choose 1, 2, or 3.")
                continue
            choice = int(choice)
            if choice == 1:
                user_id, token = await sign_up()
            elif choice == 2:
                user_id, token = await log_in()
            elif choice == 3:
                break

            if user_id is not None and token != "":
                while True:
                    contacts = await get_previous_contacts(user_id, token)
                    if contacts:
                        print("Previous Chats:")
                        for contact in contacts:
                            print(contact)
                    else:
                        print("No previous chats found.")
                    print("\n1. Previous Chat\n2. New Chat\n3. Chat With AI\n4. Exit")
                    chat_choice = input("Select: ")
                    if chat_choice == "1":
                        contact_username = input("Select contact: ")
                        if contact_username not in contacts:
                            print("You have not chatted with this user before.")
                            continue
                        await chat(user_id, token, contact_username, False)
                    elif chat_choice == "2":
                        contact_username = input("Enter username of new contact: ")
                        if contact_username in contacts:
                            print("You have already chatted with this user.")
                            continue
                        await chat(user_id, token, contact_username, True)
                    elif chat_choice == "3":
                        await chat_with_ai(user_id, token)
                    elif chat_choice == "4":
                        break
                    else:
                        print("Invalid selection. Please choose 1, 2, 3, or 4.")
        except Exception as e:
            print(f"Unexpected error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
