import logging
import threading
from config import load_config
from plurk_oauth import PlurkAPI
from PlurkPostResponse import PlurkPostResponse
from PlurkDailyPost import PlurkDailyPost
from GenerateContentResponse import GenerateContentResponse

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

    content_response = GenerateContentResponse(gemini_api_key)
    bot = PlurkPostResponse(plurk_api, content_response)
    daily_post = PlurkDailyPost(plurk_api)

    logging.info("啟動 PlurkBot")

    # 使用多線程來同時執行 daily_post.schedule_daily_post() 和 bot.run()
    daily_post_thread = threading.Thread(target=daily_post.schedule_daily_post)
    bot_thread = threading.Thread(target=bot.run)

    daily_post_thread.start()
    bot_thread.start()

    # 等待這兩個子線程結束
    daily_post_thread.join()
    bot_thread.join()

if __name__ == "__main__":
    main()