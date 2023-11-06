# Promptivity
Primptivity is a cross browser extension that aims to reduce the amount of time wasted on social media sites such as Netflix or Instagram. It does this by blocking the user from accessing these websites until they give a reason for using it. It stores this data and sends you a report on how you can spend your time and gives some suggestions on how you can waste less time.
## Features

- Pop up that blocks you from unproductive websites
- Asks you for a reason for being on the website befor giving you access
- Records the the reason, website you were on, and how long you were on it
- Uses the infomation stored to build a report on how you spent your time and give suggestions on how you can reduce time on these websites


## Installation

Must Have:
- Node.js 10 or later installed
- Yarn v1 or 2 installed

Run the following:
 - ``` yarn install``` to to install dependencies
 - ``` yarn run dev:chrome``` to start the development server for chrome extension
 - ``` yarn run dev:firefox``` to start the development server for firefox extension
 - ``` yarn run dev:opera``` to start the development server for opera extension
 - ``` yarn run build``` builds and packs extensions all at once to extension/ directory
    
To install the backend: \
Navigate to the backend source with:
 - ```cd sourca_back```

Create a new virtual envirument with:
 - ```python -m venv venv```
 - Activate it.

Install requirements with:
 - ```pip install -r requirements.txt```
