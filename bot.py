import os
import logging
from pyrogram.errors import FloodWait, PeerIdInvalid, RPCError
import asyncio
from dotenv import load_dotenv
from pyrogram import Client, filters
from pyrogram.types import Message

# Load environment variables from .env file
load_dotenv()
SESSION_STRING = os.getenv("SESSION_STRING")

User = Client(name="AcceptUser", session_string=SESSION_STRING)

# Main Process to Approve Join Requests
@User.on_chat_join_request(filters.group | filters.channel & ~filters.private)
async def approve_chat_join_request_handler(_, m: Message):
    try:
        # Approve the join request
        await User.approve_chat_join_request(m.chat.id, m.from_user.id)
        logging.info(f"Join request approved for {m.from_user.id}")

    except PeerIdInvalid:
        logging.error(f"Invalid peer ID for chat {m.chat.id}. The bot might not have access.")
    except FloodWait as e:
        logging.warning(f"FloodWait: sleeping for {e.value} seconds.")
        await asyncio.sleep(e.value)
    except RPCError as e:
        logging.error(f"RPCError: {str(e)}")
    except Exception as err:
        logging.error(f"Unexpected error: {err}")

# Command to approve join requests in a loop
@User.on_message(filters.command(["run", "approve"], [".", "/"]))
async def approve(client, message):
    chat_id = message.chat.id
    await message.delete()

    try:
        while True:  # Loop to approve requests
            try:
                await client.approve_all_chat_join_requests(chat_id)
            except FloodWait as t:
                logging.info(f"FloodWait for {t.value} seconds. Sleeping...")
                await asyncio.sleep(t.value)
            except PeerIdInvalid:
                logging.error(f"Invalid peer ID: {chat_id}. Skipping this chat.")
                break  # Exit the loop if chat ID is invalid
            except RPCError as e:
                logging.error(f"RPCError: {str(e)}")
            except Exception as e:
                logging.error(f"Unexpected error: {str(e)}")
                break
    except FloodWait as s:
        logging.info(f"FloodWait for {s.value} seconds. Sleeping...")
        await asyncio.sleep(s.value)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Bot is running!")
    User.run()
