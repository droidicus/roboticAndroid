import asyncio
import datetime
import json
import sys
import time

import discord
import pandas as pd
from tqdm import tqdm

# Constants and such
NOW = datetime.datetime.utcnow()
# LOOKBACK_AFTER = None
# LOOKBACK_AFTER = NOW - datetime.timedelta(days=365)
# LOOKBACK_AFTER = NOW - datetime.timedelta(days=30)
# LOOKBACK_AFTER = NOW - datetime.timedelta(days=7)
LOOKBACK_AFTER = NOW - datetime.timedelta(days=1)
# LOOKBACK_AFTER = NOW - datetime.timedelta(hours=1)
FILE_NAME = 'test'
OUTPUT_DATA_FILE = f'{FILE_NAME}_data.parquet'
OUTPUT_METADATA_FILE = f'{FILE_NAME}_meta.parquet'
FILE_VERSION = 'pre-0.0.0'

# Where the roboticAndroid lives
client = discord.Client()

@client.event
async def on_disconnect():
    print('INFO: Recieved `on_disconnect` event!')

@client.event
async def on_ready():
    def message_to_dict(msg):
        return {
            'author': str(msg.author),
            'author_name': msg.author.name,
            'author_displayname': msg.author.nick if msg.author == discord.member.Member else '',
            'author_id': msg.author.id,
            'content': msg.content,
            'chanel': str(msg.channel),
            'channel_name': msg.channel.name,
            'channel_id': msg.channel.id,
            # 'mentions': msg.mentions,
            'guild': str(msg.guild),
            'guild_name': msg.guild.name,
            'guild_id': msg.guild.id,
            # 'reactions': msg.reactions,
            'type': str(msg.type),
            'creation_datetime': msg.created_at,
        }

    print(f'We have logged in as {client}')

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
                        channel_elem_dict_list.append(message_to_dict(elem))

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
    print(f'Parsing speed: {total_messages/(then-NOW).total_seconds():.2f} msg/sec')

    # Save data and metadata to parquet files
    print('')
    print(f'Saving data to - {OUTPUT_DATA_FILE}')
    data.to_parquet(OUTPUT_DATA_FILE)
    print(f'Saving metadata to - {OUTPUT_METADATA_FILE}')
    pd.DataFrame([{
        'file_version': FILE_VERSION,
        'start_datetime': LOOKBACK_AFTER,
        'end_datetime': NOW,
        'collection_datetime': then,
        }]).to_parquet(OUTPUT_METADATA_FILE)

    # Close the bot when we are complete, this exits the bot
    print('')
    print('DONE!')
    await client.close()
    print('Closing loop, bot shutting down.')

# # This method is called for each new message that the bot can see
# @client.event
# async def on_message(message):
#     print(message)
#     # print(f'{message.channel} - {message.author}: {message.content}')

if __name__ == "__main__":
    # Read the secret token from disk, change this file to contain your token
    with open('token', 'r') as f:
        token = f.readline()

    # Bring the bot to life
    print('Starting up bot...')
    client.run(token)
