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

# Command to approve all pending join requests on the /run command
@User.on_message(filters.command(["run", "approve"], [".", "/"]))
async def approve(client, message):
    chat_id = message.chat.id
    await message.delete()

    try:
        # Get the list of all pending join requests at this moment
        pending_requests = client.get_chat_join_requests(chat_id)  # This is an async generator
        
        # Iterate over the async generator and process each request
        async for request in pending_requests:
            try:
                # Access the user object from the ChatJoiner object
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

        # Send a confirmation message after processing all pending requests
        # msg = await client.send_message(chat_id, "Approved all pending join requests as of this command.")  # Wait before deleting the confirmation message
        # await msg.delete()

    except FloodWait as e:
        logging.info(f"FloodWait for {e.value} seconds. Sleeping...") 
        await asyncio.sleep(e.value)
    except PeerIdInvalid:
        logging.error(f"Invalid chat ID: {chat_id}. Cannot approve join requests.")
    except RPCError as e:
        logging.error(f"RPCError: {str(e)}")
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Bot is running!")
    User.run()
