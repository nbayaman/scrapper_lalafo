import asyncio
from telethon import TelegramClient, functions, types
from telethon.errors import SessionPasswordNeededError, FloodWaitError
import time

# Your credentials
api_id = YOUR_API_ID  # Replace with your api_id (integer)
api_hash = 'YOUR_API_HASH'  # Replace with your api_hash (string)
phone = '+YOUR_PHONE_NUMBER'  # Your Telegram phone number
channel_username = 'your_channel_username'  # Or use channel ID as int (e.g., -1001234567890)

# Path to your numbers file
numbers_file = 'numbers.txt'

# Batch size (keep small to avoid bans)
batch_size = 10

async def main():
    client = TelegramClient('session', api_id, api_hash)
    await client.start(phone=phone)

    # Load phone numbers
    with open(numbers_file, 'r') as f:
        phones = [line.strip() for line in f if line.strip()]

    # Resolve channel entity once
    channel = await client.get_entity(channel_username)

    imported_users = []

    # Import contacts in batches
    for i in range(0, len(phones), batch_size):
        batch = phones[i:i + batch_size]
        contacts = [types.InputPhoneContact(client_id=0, phone=p, first_name='Bulk', last_name='Contact') for p in batch]

        try:
            result = await client(functions.contacts.ImportContactsRequest(contacts))
            # Filter users who exist on Telegram
            existing_users = [u for u in result.users if u]
            imported_users.extend(existing_users)
            print(f"Imported {len(existing_users)} users from batch starting at {i}")
        except FloodWaitError as e:
            print(f"Flood wait: Sleeping for {e.seconds} seconds")
            await asyncio.sleep(e.seconds)
        except Exception as e:
            print(f"Error importing batch: {e}")

        # Pause to avoid rate limits
        await asyncio.sleep(10)  # Adjust as needed

    # Invite imported users to channel in batches
    for i in range(0, len(imported_users), batch_size):
        batch_users = imported_users[i:i + batch_size]

        try:
            await client(functions.channels.InviteToChannelRequest(
                channel=channel,
                users=batch_users
            ))
            print(f"Invited {len(batch_users)} users to channel from batch starting at {i}")
        except FloodWaitError as e:
            print(f"Flood wait: Sleeping for {e.seconds} seconds")
            await asyncio.sleep(e.seconds)
        except Exception as e:
            print(f"Error inviting batch: {e}")

        await asyncio.sleep(10)  # Pause

    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
