import schedule
import time
from datetime import datetime #, timedelta
# import pytz
import logging

class PlurkDailyPost:
    def __init__(self, plurk_api):
        self.plurk = plurk_api
        self.last_post_date = None 

    def post_daily_message(self):
        # 獲取當前日期並格式化為 年/月/日
        current_date = datetime.now().strftime("%Y/%m/%d")
        
        # 判斷今天是否已發文
        if self.last_post_date == current_date:
            logging.info("今天已發過每日貼文，跳過。")
            return
        self.last_post_date = current_date

        content = f"{current_date} 機器人生存確認，多喝熱水 (draw)"
        logging.info(f"機器人生存確認發噗: {content}")
        self.plurk.callAPI('/APP/Timeline/plurkAdd', {
            'content': content,
            'qualifier': 'says'
        })

    def schedule_daily_post(self):

        # 每日發文
        schedule.every().day.at("18:00").do(self.post_daily_message)

        # 等待並執行排程
        while True:
            schedule.run_pending()
            time.sleep(1)