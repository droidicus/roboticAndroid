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
# LOOKBACK_AFTER = NOW - datetime.timedelta(days=1)
LOOKBACK_AFTER = NOW - datetime.timedelta(hours=1)
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
    print('We have logged in as {0.user}'.format(client))
    data = pd.DataFrame()
    # total_msg_count = 0
    for guild in client.guilds:
        for channel in guild.channels:
            # channel_msg_count = 0
            channel_elem_dict_list = []
            if channel.permissions_for(member=guild.me).view_channel:
                if type(channel) != discord.channel.VoiceChannel and\
                   type(channel) != discord.channel.CategoryChannel:
                    # Don't process channels without text
                    print(f'\n**** Processing channel: {channel} ****')

                    # Process each element in the history
                    with tqdm(unit_scale=True, desc=f'Messages processed so far in {channel}') as pbar:
                        async for elem in channel.history(limit=None, after=LOOKBACK_AFTER, before=NOW):
                            # update bar
                            pbar.update(1)

                            # Add dict of data to the list
                            channel_elem_dict_list.append({
                                'author': str(elem.author),
                                'author_name': elem.author.name,
                                'author_displayname': elem.author.nick if elem.author == discord.member.Member else '',
                                'author_id': elem.author.id,
                                'content': elem.content,
                                'chanel': str(elem.channel),
                                'channel_name': elem.channel.name,
                                'channel_id': elem.channel.id,
                                # 'mentions': elem.mentions,
                                'guild': str(elem.guild),
                                'guild_name': elem.guild.name,
                                'guild_id': elem.guild.id,
                                # 'reactions': elem.reactions,
                                'type': str(elem.type),
                                'creation_datetime': elem.created_at,
                            })

                        # Channel complete, append data to dataframe
                        data = data.append(channel_elem_dict_list, ignore_index=True)

    # Info banner
    then = datetime.datetime.utcnow()
    print(f'\nProcessing took: {then-NOW}')
    print('*******************************************************************')
    print(f'Report for {LOOKBACK_AFTER} to {NOW}')
    print('*******************************************************************')

    # Save data and metadata to parquet files
    print(f'\nSaving data to - {OUTPUT_DATA_FILE}')
    data.to_parquet(OUTPUT_DATA_FILE)
    pd.DataFrame([{
        'file_version': FILE_VERSION,
        'start_datetime': LOOKBACK_AFTER,
        'end_datetime': NOW,
        'collection_datetime': then,
        }]).to_parquet(OUTPUT_METADATA_FILE)

    # Close the bot when we are complete, this exits the bot
    print('\nDONE!')
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
    client.run(token)
