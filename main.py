################################################################################################
# Libraries #

import os
import argparse
import subprocess
import zipfile

from rich import json
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import MessageMediaDocument, MessageMediaPhoto, MessageMediaWebPage, WebPageEmpty
from rich.console import Console

# This package will handle cli  from the telegram group
from tqdm import tqdm

################################################################################################

# Argument Parsing #

parser = argparse.ArgumentParser(description='Telegram File Fetcher and Handler')
parser.add_argument('--api-id', type=int, help='REQUIRED - API ID of the Telegram API')
parser.add_argument('--api-hash', type=str, help='REQUIRED - API Hash of the Telegram API')
parser.add_argument('--channel-id', type=int, help='REQUIRED - Channel ID of the Telegram Channel')
parser.add_argument('--limit', type=int, help='Number of messages to fetch from the channel - Default: 100')
parser.add_argument('--file-size-limit', type=int, help='File size limit in bytes to download files from the channel '
                                                        '- Default: 10MB')
parser.add_argument('--output-dir', type=str, help='Output directory to save the downloaded files - Default: '
                                                   './Files')
parser.add_argument('--log-file', type=str, help='Log file to save the logs - Default: ./logs.log')
parser.add_argument('-c', '--process-compressed-files', action='store_true', help='Decompress the zip files in the '
                                                                                  'output'
                                                                                  'directory')
args = parser.parse_args()

# Rich Text Formatting #
console = Console()


################################################################################################
# Functions #

# Connect and Log-in/Sign-in to telegram API to download media files into the local directory
def tlg_fetch(api_id, api_hash, channel_id, limit=100, file_size_limit=10 * 1024 * 1024,
              output_dir='./Files'):
    # Check if the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    print("Starting...\n\n")
    with TelegramClient('Session', api_id, api_hash) as client:
        # Get the channel information
        channel = client(GetFullChannelRequest(channel_id))

        # Get the messages from the channel
        messages = client.get_messages(channel.full_chat, limit=limit)
        # ________________________________________________^^^^^^^^^^^  <-- Change this to the number of messages you want to iterate through or remove to process all messages

        # Initialize the count of downloaded files
        count_downloaded_files = 0

        message_index = {}
        # Check if there are messages in the channel
        if messages:
            print(f'Started fetching files from the channel {channel.chats[0].title}...\n')
            # Loop through the messages and download the files
            for message in tqdm(messages):
                if isinstance(message.media, MessageMediaDocument) and message.media.document.size < file_size_limit:
                    # _________________________________________________^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  <-- Change this to the file size limit you want or remove to download all files
                    message_index[message.media.document.id] = message.media.document.attributes[0].file_name
                    file_path = f'{output_dir}/{message.media.document.attributes[0].file_name}'
                    if not os.path.exists(file_path) and message.media.document.attributes[0].file_name.replace('.zip',
                                                                                                                '') not in os.listdir(
                            f'{output_dir}/'):
                        count_downloaded_files += 1
                        tqdm(message.download_media(f'{output_dir}/'))
                elif isinstance(message.media, MessageMediaPhoto):
                    message_index[message.media.photo.id] = message.media.photo.id
                    file_path_photo = f'{output_dir}/photos/{message.media.photo.id}.jpg'
                    if not os.path.exists(file_path_photo):
                        message.download_media(file_path_photo)
                        count_downloaded_files += 1
                elif isinstance(message.media, MessageMediaWebPage):
                    message_index[message.media.webpage.id] = message.media.webpage.url
                    file_path_webpage = f'{output_dir}/webpages/{message.media.webpage.site_name}'
                    if not os.path.exists(file_path_webpage):
                        if not message.download_media(file_path_webpage):
                            pass
                        else:
                            count_downloaded_files += 1

            if count_downloaded_files > 0:
                print(
                    f'\n{count_downloaded_files} files downloaded successfully from the {channel.chats[0].title} channel.')
            else:
                print(f'\nEverything is up-to-date.\n')
        else:
            print('No messages found in the channel id. Check if your account joined the channel.\n')
            return None
        return message_index


def decompress_zip(zip_file_path):
    zip_folder = zip_file_path.replace('.zip', '')
    try:
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            os.mkdir(zip_folder)  # Create a directory with the same name as the zip file
            print('Extracting files...\n')
            if zip_ref.testzip() is not None:
                print(f'Error: {zip_file_path} is corrupted.')
                return
            else:
                zip_ref.extractall(zip_folder)  # Extract the zip file to the directory
        # os.remove(zip_file_path)
        print(f'Successfully decompressed {zip_file_path} into {zip_folder}.\n')
    except FileNotFoundError:
        print(f'Error: {zip_file_path} not found.')
    except zipfile.BadZipFile:
        print(f'Error: {zip_file_path} is not a zip file.')
    except RuntimeError:
        print(f'Error: {zip_file_path} is encrypted, password required for extraction.')


def zip_files_extract(output_dir):
    # Get the zip files in the output directory
    zip_files = [f for f in os.listdir(output_dir) if
                 f.endswith('.zip')]  # or f.endswith('.rar') or f.endswith('.7z') or f.endswith('.gz')]
    if not zip_files:
        print('No zip files found in the output directory. You\'re all set.')
    # Check if the output directory exists
    if not os.path.exists(output_dir):
        print('Error: Output directory not found.')
    for zip_file in tqdm(zip_files):
        # Check if the zip file exists
        if os.path.exists(zip_file_path := f'{output_dir}/{zip_file}'):
            # Decompress the zip file
            decompress_zip(zip_file_path)
        else:
            print(f'Error: Zip file {zip_file} not found.')
    return 'Files decompressed successfully'


################################################################################################

# Main #

def main():
    limit = 1000
    file_size_limit = 10 * 1024 * 1024
    output_dir = './Files'
    log_file = './logs.log'
    if args.api_id and args.api_hash and args.channel_id:
        if args.limit:
            limit = args.limit
        if args.file_size_limit:
            file_size_limit = args.file_size_limit
        if args.output_dir:
            output_dir = args.output_dir
        if args.log_file and args.log_file != './logs.log':
            log_file = args.log_file
        completed_process = tlg_fetch(args.api_id, args.api_hash, 1555377160, limit, file_size_limit, output_dir)
        if completed_process:
            output = json.dumps(completed_process, indent=4, sort_keys=True)
            with open(log_file, 'w') as f:
                f.write('[Success]: Log file for the Telegram File Fetcher and Handler(\n')
                f.write(output)
                f.write('\n)')
        else:
            print('\nProcess failed.')
    elif args.process_compressed_files:
        zip_files_extract(output_dir)
    else:
        print('Error: Please provide the required arguments: --api-id, --api-hash, --channel-id \n Or -z to extract '
              'zip files ')


if __name__ == "__main__":
    main()
