import asyncio
import datetime
import json
import sys
import time
import os
from pprint import pprint

import discord
import pandas as pd
from tqdm import tqdm

################################################################
# TODO list:
# Add incremental mode to update existing file with new messages
# Add command line options
################################################################

# Constants and such
NOW = datetime.datetime.utcnow()
# LOOKBACK_AFTER = None # ALL history! (Warning this takes a while)
# LOOKBACK_AFTER = NOW - datetime.timedelta(days=365) (Warning this takes a while)
# LOOKBACK_AFTER = NOW - datetime.timedelta(days=30)
# LOOKBACK_AFTER = NOW - datetime.timedelta(days=7)
# LOOKBACK_AFTER = NOW - datetime.timedelta(days=1)
LOOKBACK_AFTER = NOW - datetime.timedelta(hours=1)
OUTPUT_FILE_NAME = 'test'
OUTPUT_FILE_DIR = 'data'
OUTPUT_DATA_FILE = os.path.join(OUTPUT_FILE_DIR, f'{OUTPUT_FILE_NAME}_data.parquet')
OUTPUT_METADATA_FILE = os.path.join(OUTPUT_FILE_DIR, f'{OUTPUT_FILE_NAME}_meta.parquet')
FILE_VERSION = 'alpha0-0.0.0'

DO_HISTORY_ONE_SHOT = True # 'True' for history parsing, 'False' for real-time parsing


# Where the roboticAndroid lives
client = discord.Client()

# repack the interesting parts of the message
def _message_to_dict(msg):
    return {
        'attachments_len': len(msg.attachments),
        'attachments_ids': [i.id for i in msg.attachments],
        'attachments_sizes': [i.size for i in msg.attachments],
        'attachments_filenames': [i.filename for i in msg.attachments],
        'attachments_urls': [i.url for i in msg.attachments],
        'author': str(msg.author),
        'author_name': msg.author.name,
        'author_displayname': msg.author.nick if type(msg.author) == discord.member.Member else '',
        'author_id': msg.author.id,
        'content': msg.content,
        'channel_name': msg.channel.name,
        'channel_id': msg.channel.id,
        'creation_datetime': msg.created_at,
        'guild_name': msg.guild.name,
        'guild_id': msg.guild.id,
        'reactions_len': len(msg.reactions),
        'reactions_emojis': [str(i.emoji) for i in msg.reactions],
        'reactions_counts': [i.count for i in msg.reactions],
        'type': str(msg.type),
        # This slows down history parsing a LOT due to the await'ed call to get all of the users,
        # up to an order of magnitude slowdown on heavily-reactioned channels. May not be needed?
        # 'reactions_userids': [[k.id for k in j] for j in [await i.users().flatten() for i in msg.reactions]],
    }

@client.event
async def on_disconnect():
    print('INFO: Recieved `on_disconnect` event!')

@client.event
async def on_ready():
    print(f'We have logged in as {client}')

    if not DO_HISTORY_ONE_SHOT:
        return

    # Start gathering all of the data
    total_messages = 0
    data = pd.DataFrame()
    for guild in client.guilds:
        # Go through each guild (server)
        for channel in guild.text_channels:
            # Go through each text_channel
            channel_elem_dict_list = []
            if channel.permissions_for(member=guild.me).view_channel:
                # If we have access to the channel (will error if you attempt to get history from any channel you don't have access to)
                print('')
                print(f'**** Processing channel: {channel} ****')

                # Process each element in the history, with a nice progress indicator
                with tqdm(unit_scale=True, desc=f'Messages processed so far in {channel}') as pbar:
                    async for elem in channel.history(limit=None, after=LOOKBACK_AFTER, before=NOW):
                        # update bar and count
                        pbar.update(1)
                        total_messages += 1

                        # Add dict of data to the list
                        elem_dict = _message_to_dict(elem)
                        channel_elem_dict_list.append(elem_dict)

                    # Channel complete, append data to dataframe
                    data = data.append(channel_elem_dict_list, ignore_index=True)

    # Info banner
    then = datetime.datetime.utcnow()
    print('')
    print('*******************************************************************')
    print(f'Report for {LOOKBACK_AFTER} to {NOW}')
    print('*******************************************************************')
    print(f'Processing took: {then-NOW}')
    print(f'Total messages parsed: {total_messages}')
    print(f'Parsing speed avg: {total_messages/(then-NOW).total_seconds():.2f} msg/sec')

    # Save data and metadata to parquet files
    os.makedirs('data', exist_ok=True)
    print('')
    print(f'Saving data to - {OUTPUT_DATA_FILE}')
    data.to_parquet(OUTPUT_DATA_FILE, compression='gzip')
    print(f'Saving metadata to - {OUTPUT_METADATA_FILE}')
    pd.DataFrame([{
        'file_version': FILE_VERSION,
        'start_datetime': LOOKBACK_AFTER,
        'end_datetime': NOW,
        'collection_datetime': then,
        }]).to_parquet(OUTPUT_METADATA_FILE, compression=None)

    # Close the bot when we are complete, this exits the bot
    print('')
    print('DONE!')
    await shutdown(client.loop)

# This method is called for each new message that the bot can see
@client.event
async def on_message(message):
    if DO_HISTORY_ONE_SHOT:
        return

    message_dict = _message_to_dict(message)

    print('')
    print(message)
    pprint(message_dict, indent=4)

# Hand exceptions
def handle_exception(loop, context):
    # context["message"] will always be there; but context["exception"] may not
    msg = context.get("exception", context["message"])
    print('')
    print(f"Caught exception: {msg}")
    print("Shutting down...")
    asyncio.create_task(shutdown(loop))

# Shutdown the application
async def shutdown(loop, signal=None):
    """Cleanup tasks tied to the service's shutdown."""
    if signal:
        print(f"Received exit signal {signal.name}...")
    # <-- snip -->
    print('Closing loop, bot shutting down.')
    await client.close()

# Let's get started
if __name__ == "__main__":
    # Setup exception handling
    client.loop.set_exception_handler(handle_exception) # TODO: This doesn't seem to be working...

    # Read the secret token from disk, change this file to contain your token
    with open('token', 'r') as f:
        token = f.readline()

    # Bring the bot to life
    print('Starting up bot...')
    client.run(token)
