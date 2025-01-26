# Plurk Bot

## Overview
This project is a Plurk bot that interacts with the Plurk API to automate responses based on specified conditions. It is designed to listen for new posts from friends and reply accordingly.

## Project Structure
```
plurk-bot
├── src
│   ├── bot.py          # Main entry point for the Plurk bot
│   ├── config.py       # Handles configuration settings
│   ├── plurk_api.py    # Interacts with the Plurk API
│   └── utils.py        # Utility functions for various tasks
├── .env                # Environment variables for development
├── config.ini          # Configuration file for sensitive tokens
├── requirements.txt     # Project dependencies
└── README.md           # Project documentation
```

## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd plurk-bot
   ```

2. **Create a Virtual Environment**
   It is recommended to use a virtual environment to manage dependencies.
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**
   Install the required packages listed in `requirements.txt`.
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**
   Create a `.env` file in the root directory and add any necessary environment variables.

5. **Set Up Configuration File**
   Create a `config.ini` file to store your sensitive tokens and configurations. Ensure it includes sections for API tokens.

## Usage
To run the bot, execute the following command:
```bash
python src/bot.py
```

## Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.