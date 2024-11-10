

import os
import logging
import asyncio
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, PeerIdInvalid, RPCError
from dotenv import load_dotenv
from fastapi import FastAPI

# Load environment variables from .env file
load_dotenv()
SESSION_STRING = os.getenv("SESSION_STRING")
PORT = int(os.getenv("PORT", 8000))

app = FastAPI()
User = Client(name="AcceptUser", session_string=SESSION_STRING)

@User.on_message(filters.command(["run", "approve"], [".", "/"]))
async def approve(client, message):
    chat_id = message.chat.id
    await message.delete()

    try:
        # Check if the bot can access the chat
        try:
            chat = await client.get_chat(chat_id)
        except PeerIdInvalid:
            logging.error(f"Invalid chat ID: {chat_id}. Skipping.")
            return

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
        logging.error(f"Unexpected error: {str(e)}")

@app.get("/")
async def root():
    return {"status": "Bot is running!"}

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Bot is running!")
    User.start()  # Starts the bot
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)

