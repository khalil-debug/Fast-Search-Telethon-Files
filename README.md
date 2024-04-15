# Telegram File Fetcher and Handler

This project is a Python script that fetches files from a specified Telegram channel, handles them, and provides a search functionality. It's still a work in progress and will be updated with more features.

## Requirements

- Python 3.10
- Telethon
- tqdm
- rich
- pandas
- FastAPI
- uvicorn
- Jinja2
- pyarrow

## Usage

1. Clone the repository `git clone https://github.com/khalil-debug/Fast-Search-Telethon-Files.git`.
2. Initialize a virtual environment with the command `python -m venv venv` then `.\venv\Scripts\activate`.
3. Install the required Python packages from requirements.txt with the command `pip install -r requirements.txt`
4. Run the `data_search.py` script with the required arguments.

## Arguments

- `--api-id`: API ID of the Telegram API.
- `--api-hash`: API Hash of the Telegram API.
- `--channel-id`: Channel ID of the Telegram Channel.
- `--limit`: Number of messages to fetch from the channel. Default is 100.
- `--file-size-limit`: File size limit in bytes to download files from the channel. Default is 10MB.
- `--output-dir`: Output directory to save the downloaded files. Default is ``./Files``.
- `--log-file`: Log file to save the logs. Default is ./logs.log.
- `-c or --process-compressed-files`: Decompress the zip files from the input directory into the same directory. Default is False.
- `-s or --search`: Search for a compromised password on the files located the input directory.


## Fetch Files

The script fetches files from the specified Telegram channel and saves them in the specified output directory. The files are saved in the following format:
    
    ```documents, photos, and zip files``` 

To fetch files from the Telegram channel, run the following command:

```bash
python main.py [REQUIRED] --api-id YOUR_API_ID --api-hash YOUR_API_HASH --channel-id YOUR_CHANNEL_ID [OPTIONAL] --output-dir YOUR_OUTPUT_DIR --file-size-limit YOUR_FILES_SIZE_LIMIT --limit YOUR_MESSAGES_NUMBER_LIMIT --log-file YOUR_LOG_FILE_OUTPUT
```


## Search Files

Once the files are fetched, you can search for a compromised password in the files' content by running the following command:

```bash 
python main.py -s --output-dir YOUR_OUTPUT_DIR
```