import logging
from config import load_config
from plurk_bot import PlurkBot

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    logging.info("載入配置")
    config = load_config()
    plurk_api_key = config['PLURK']
    gemini_api_key = config['GEMINI']['api_key']
    # print(gemini_api_key)
    bot = PlurkBot(
        plurk_api_key['consumer_key'],
        plurk_api_key['consumer_secret'],
        plurk_api_key['token'],
        plurk_api_key['token_secret'],
        gemini_api_key  
    )
    logging.info("啟動 PlurkBot")
    bot.run()

if __name__ == "__main__":
    main()