import os
from dotenv import load_dotenv
from pyrogram.types import Message
from pyrogram import filters, Client, errors
from pyrogram.errors import FloodWait, PeerIdInvalid, RPCError
import asyncio
import logging

# Load environment variables from .env file
load_dotenv()

# Get session string from environment variable
SESSION_STRING = os.getenv("SESSION_STRING")

# Initialize the User client
User = Client(name="AcceptUser", session_string=SESSION_STRING)

# Main Process to Approve Join Requests
@User.on_chat_join_request(filters.group | filters.channel & ~filters.private)
async def approve_chat_join_request_handler(_, m: Message):
    try:
        # Check if bot has the necessary permissions in the chat
        chat_member = await User.get_chat_member(m.chat.id, "me")
        if not chat_member.can_invite_users:
            logging.error("Bot lacks permission to approve join requests.")
            return
        
        # Approve the join request
        await User.approve_chat_join_request(m.chat.id, m.from_user.id)
        logging.info(f"Join request approved for {m.from_user.id}")

        # Send a direct message (DM) to the user
        try:
            await User.send_message(
                m.from_user.id,
                f"**Hello {m.from_user.mention}!**\nWelcome to {m.chat.title}. Enjoy your stay! 😄"
            )
            logging.info(f"DM sent to {m.from_user.id}")
        except PeerIdInvalid:
            logging.error(f"Cannot send DM to {m.from_user.id}. They might have DMs disabled.")
    except FloodWait as e:
        logging.warning(f"FloodWait: sleeping for {e.value} seconds.")
        await asyncio.sleep(e.value)
    except RPCError as e:
        # Ignore the RPCError and log it instead of exiting
        logging.error(f"RPCError: {str(e)}")
    except Exception as err:
        logging.error(f"Error approving join request for {m.from_user.id}: {err}")

@User.on_message(filters.command(["run", "approve"], [".", "/"]))
async def approve(client, message):
    Id = message.chat.id
    await message.delete(True)

    try:
        while True:  # Loop to approve requests
            try:
                await client.approve_all_chat_join_requests(Id)
            except FloodWait as t:
                logging.info(f"FloodWait for {t.value} seconds. Sleeping...")
                await asyncio.sleep(t.value)
            except RPCError as e:
                # Ignore the RPCError and log it instead of exiting
                logging.error(f"RPCError: {str(e)}")
            except Exception as e:
                logging.error(f"Error: {str(e)}")
                break  # Stop if an unexpected error occurs
    except FloodWait as s:
        logging.info(f"FloodWait for {s.value} seconds. Sleeping...")
        await asyncio.sleep(s.value)
        while True:  # Retry after waiting
            try:
                await client.approve_all_chat_join_requests(Id)
            except FloodWait as t:
                logging.info(f"FloodWait for {t.value} seconds. Sleeping...")
                await asyncio.sleep(t.value)
            except RPCError as e:
                # Ignore the RPCError and log it instead of exiting
                logging.error(f"RPCError: {str(e)}")
            except Exception as e:
                logging.error(f"Error: {str(e)}")
                break

    # Send completion message
    msg = await client.send_message(Id, "**Task Completed** ✓ **Approved Pending All Join Requests**")
    await msg.delete()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Bot is running!")
    User.run()  # Run User client
