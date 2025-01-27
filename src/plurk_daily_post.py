import schedule
import time
from datetime import datetime, timedelta
import pytz
import logging

class DailyPost:
    def __init__(self, plurk_api):
        self.plurk = plurk_api

    def post_daily_message(self):
        # 獲取當前日期並格式化為 年/月/日
        current_date = datetime.now().strftime("%Y/%m/%d")
        content = f"{current_date} 機器人生存確認，多喝熱水 (draw)"
        logging.info(f"機器人生存確認發噗: {content}")
        self.plurk.callAPI('/APP/Timeline/plurkAdd', {
            'content': content,
            'qualifier': 'says'
        })

    def schedule_daily_post(self):
        # 設定台灣時區
        taiwan_tz = pytz.timezone('Asia/Taipei')
        now = datetime.now(taiwan_tz)
        target_time = now.replace(hour=16, minute=0, second=0, microsecond=0)

        # 如果當前時間已過目標時間，則設定為明天的目標時間
        if now > target_time:
            target_time += timedelta(days=1)

        # # 計算等待時間
        # wait_time = (target_time - now).total_seconds()
        # logging.info(f"等待 {wait_time} 秒後發布每日貼文")

        # 每日發文
        schedule.every().day.at("15:20").do(self.post_daily_message)

        # 等待並執行排程
        while True:
            schedule.run_pending()
            time.sleep(1)