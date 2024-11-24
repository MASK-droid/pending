import os
import logging
import asyncio
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, PeerIdInvalid, RPCError
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# Load environment variables from .env file
load_dotenv()
SESSION_STRING = os.getenv("SESSION_STRING")
PORT = int(os.getenv("PORT", 8000))

# Initialize Flask app
app = Flask(__name__)
User = Client(name="AcceptUser", session_string=SESSION_STRING)

@app.route("/")
def home():
    return {"status": "Bot is running!"}

@User.on_message(filters.command(["run", "approve"], [".", "/"]))
async def approve(client, message):
    chat_id = message.chat.id
    await message.delete()

    try:
        # Validate the chat ID
        try:
            chat = await client.get_chat(chat_id)
            logging.info(f"Chat details: ID={chat.id}, Title={chat.title}")
        except PeerIdInvalid:
            logging.error(f"Invalid chat ID: {chat_id}. Skipping.")
            return
        except Exception as e:
            logging.error(f"Error retrieving chat: {str(e)}")
            return

        # Process pending join requests
        try:
            pending_requests = client.get_chat_join_requests(chat_id)
            async for request in pending_requests:
                try:
                    user = request.user
                    await client.approve_chat_join_request(chat_id, user.id)
                    logging.info(f"Approved join request for user {user.id}")
                except FloodWait as e:
                    logging.warning(f"FloodWait: sleeping for {e.value} seconds.")
                    await asyncio.sleep(e.value)
                except PeerIdInvalid:
                    logging.error(f"Invalid peer ID: {request.user.id}. Cannot approve join request.")
                except RPCError as e:
                    logging.error(f"RPCError: {str(e)}")
                except Exception as err:
                    logging.error(f"Unexpected error for user {request.user.id}: {err}")
        except Exception as e:
            logging.error(f"Error processing pending join requests: {str(e)}")

    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")

def run_flask():
    """Runs Flask in a separate thread."""
    app.run(host="0.0.0.0", port=PORT)



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Starting Flask server and Telegram bot...")

    # Start Flask server in a separate thread
    flask_thread = Thread(target=run_flask)
    flask_thread.start()

    # Run the bot in the main thread
    User.run()
