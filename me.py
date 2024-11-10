import os
import logging
from pyrogram.errors import FloodWait, PeerIdInvalid, RPCError
import asyncio
from dotenv import load_dotenv
from pyrogram import Client, filters
from pyrogram.types import Message


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

# Command to approve all pending join requests on the /run command
@User.on_message(filters.command(["run", "approve"], [".", "/"]))
async def approve(client, message):
    chat_id = message.chat.id
    await message.delete()

    try:
        # Get the list of all pending join requests at this moment
        pending_requests = [request async for request in client.get_chat_join_requests(chat_id)]
        
        # If there are no pending requests, notify and exit
        if not pending_requests:
            msg = await client.send_message(chat_id, "No pending join requests to approve.")
            await asyncio.sleep(5)
            await msg.delete()
            return

        # Approve each pending request individually
        for request in pending_requests:
            try:
                await client.approve_chat_join_request(chat_id, request.from_user.id)
                logging.info(f"Approved join request for user {request.from_user.id}")
            except FloodWait as e:
                logging.warning(f"FloodWait: sleeping for {e.value} seconds.")
                await asyncio.sleep(e.value)
            except PeerIdInvalid:
                logging.error(f"Invalid peer ID: {request.from_user.id}. Cannot approve join request.")
            except RPCError as e:
                logging.error(f"RPCError: {str(e)}")
            except Exception as err:
                logging.error(f"Unexpected error for user {request.from_user.id}: {err}")

        # Send a confirmation message after processing all pending requests
        msg = await client.send_message(chat_id, "Approved all pending join requests as of this command.")
        await asyncio.sleep(5)  # Wait before deleting the confirmation message
        await msg.delete()

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