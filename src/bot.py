import logging
from config import load_config
from plurk_oauth import PlurkAPI
from plurk_response import PlurkResponse
from plurk_daily_post import DailyPost
from response_content import ContentResponse

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    logging.info("載入配置")
    config = load_config()
    plurk_api_key = config['PLURK']
    gemini_api_key = config['GEMINI']['api_key']

    plurk_api = PlurkAPI(
        plurk_api_key['consumer_key'],
        plurk_api_key['consumer_secret']
    )
    plurk_api.authorize(
        plurk_api_key['token'],
        plurk_api_key['token_secret']
    )

    content_response = ContentResponse(gemini_api_key)
    bot = PlurkResponse(plurk_api, content_response)
    daily_post = DailyPost(plurk_api)

    logging.info("啟動 PlurkBot")
    daily_post.schedule_daily_post()
    bot.run()

if __name__ == "__main__":
    main()