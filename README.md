# Gmail-to-CSV

I personally find Gmail API to be a bit confusing for beginners. The API’s wizard comes handy to create the project, get credentials, and authenticate them. However, the process that should be followed after that is not mentioned clearly.

Therefore, I have created a Python script that does the following:
1. Scrapes all emails from your mailbox
2. Exports all emails to CSV file which includes (Sender, Subject, Message)
3. Email content is formatted using bs4


## Installation

Create a project at https://console.developers.google.com/project and save client id, project name and client secret in credentials.json file.

Run the python environment
```
source env/bin/activate
```

Run scraper.py
```
python scraper.py
```