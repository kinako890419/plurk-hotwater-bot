import logging
import re
import json
import threading
import time
import urllib.request
import random

import schedule

class PlurkPostResponse:
    """
    抓取 Plurk 的 Comet Channel 並回覆訊息
    這個class會持續運行，並在有新 Plurk 訊息時進行回覆
    """
    def __init__(self, plurk_api, content_response):
        self.plurk = plurk_api
        self.gemini_api = content_response
        self.comet_channel = None
        self.new_offset = -1
        self.jsonp_re = re.compile(r'CometChannel\.scriptCallback\((.+)\);\s*')
        self.user_status = []
        logging.info("PlurkBot 初始化完成")
        schedule.every().day.at("00:00").do(self.clear_user_status)
        threading.Thread(target=self._run_schedule, daemon=True).start()

    def clear_user_status(self):
        self.user_status.clear()
        logging.info("清空 user_status")

    def _run_schedule(self):
        while True:
            schedule.run_pending()
            time.sleep(1)
    
    def get_comet_channel(self):
        comet = self.plurk.callAPI('/APP/Realtime/getUserChannel')
        self.comet_channel = comet.get('comet_server') + "&new_offset=%d"
        logging.info("取得 Comet Channel")

    def respond_to_message(self, pid, user_id, content, qualifier):
        try:
            if "！" in content:
                content = content.replace("！", "!")
            logging.info(f"處理訊息: {content} (qualifier: {qualifier})")

            if (qualifier == 'hopes' or qualifier == 'wishes') and '!抽' in content: # 希望
                cleaned_content = content.replace(' ', '').replace('!抽', '')
                logging.info(f"清理後的內容: {cleaned_content}")
                response_parts = self.gemini_api.generate_response(cleaned_content, 'tarot')
                for part in response_parts:
                    logging.info(f"回覆內容: {part.strip()}")
                    self.plurk.callAPI('/APP/Responses/responseAdd', {
                        'plurk_id': pid,
                        'content': part.strip(),
                        'qualifier': 'thinks'
                    })
                    time.sleep(1)
            elif qualifier == 'wants' and '!抱怨' in content: # 想要
                cleaned_content = content.replace(' ', '').replace('!抱怨', '')
                logging.info(f"清理後的內容: {cleaned_content}")
                response_parts = self.gemini_api.generate_response(cleaned_content, 'bad_advice')
                for part in response_parts:
                    logging.info(f"回覆內容: {part.strip()}")
                    self.plurk.callAPI('/APP/Responses/responseAdd', {
                        'plurk_id': pid,
                        'content': part.strip(),
                        'qualifier': 'thinks'
                    })
                    time.sleep(1)
            elif qualifier == 'asks' and '!為什麼' in content: # 問
                cleaned_content = content.replace(' ', '').replace('!為什麼', '')
                logging.info(f"清理後的內容: {cleaned_content}")
                response_parts = self.gemini_api.generate_response(cleaned_content, 'rap')
                for part in response_parts:
                    logging.info(f"回覆內容: {part.strip()}")
                    self.plurk.callAPI('/APP/Responses/responseAdd', {
                        'plurk_id': pid,
                        'content': part.strip(),
                        'qualifier': 'feels'
                    })
                    time.sleep(1)
            elif (qualifier == 'hopes' or qualifier == 'wishes') and '!每日運勢' in content:
                if user_id in self.user_status:
                    logging.info(f"本日已經回覆，跳過: {user_id}")
                    self.plurk.callAPI('/APP/Responses/responseAdd', {
                        'plurk_id': pid,
                        'content': "明天再來問",
                        'qualifier': ':'
                    })
                    time.sleep(1)
                    return
                self.user_status.append(user_id)
                self.plurk.callAPI('/APP/Responses/responseAdd', {
                    'plurk_id': pid,
                    'content': random.choice(['今天運勢不錯', '今天運勢一般', "今天一切順利",
                    "今天一切順利，只要你放棄掙扎，接受命運。",
                    "今天你做什麼都會順...如果你有做點什麼的話啦。",
                    "你的今日運勢是：無法載入，請重啟你的人格。",
                    "先吃東西，其他晚點再說。",
                    "你今天像一顆鈕扣電池 — 看起來有用，但其實快沒電了。",
                    "今天一切都還行，只要你不打開訊息、不接電話、不出門。",
                    "你今天會突然有種豁然開朗的感覺，不是你開竅了，是生活終於懶得打你了。",
                    "你今天的荷包比你的人生還穩定，這是一種罕見奇蹟，請好好珍惜。",
                    "今天投資有望，但前提是你有錢可以投。",
                    "今天出門會遇到有趣的人…對方不一定這麼想。",
                    "今天老闆今天心情不錯，適合偷偷離職。",
                    "有一筆意外之財在路上……但它導航錯了，去了別人家。",
                    "好與不好之間的界線今天很模糊，建議你保持迷茫，這樣比較安全。",
                    "今日可買樂透，但只能買一張，不然就是貪。",
                    "今天早上11點37分前說出的第三句話，將影響你今天的第六餐。",
                    "今日切勿與西瓜爭辯，尤其在雨後。",
                    "不好吧",
                    "今天還行",
                    "今天宜多喝水",
                    "今天宜多喝熱水"]),
                    'qualifier': 'thinks'
                })
                time.sleep(1)
            else:
                random_num = random.randint(1, 100)

                if '機器人' in content:
                    self.plurk.callAPI('/APP/Responses/responseAdd', {
                        'plurk_id': pid,
                        'content': "蛤",
                        'qualifier': ':'
                    })
                    time.sleep(0.5)
                elif '好不好' in content or '要不要' in content:
                    random_yn = random.choice(['好', '不要', '[emo3]', '[emo4]'])
                    self.plurk.callAPI('/APP/Responses/responseAdd', {
                        'plurk_id': pid,
                        'content': random_yn,
                        'qualifier': 'feels'
                    })
                    time.sleep(0.5)
                elif '熱水' in content:
                    self.plurk.callAPI('/APP/Responses/responseAdd', {
                        'plurk_id': pid,
                        'content': '多喝熱水',
                        'qualifier': 'says'
                    })
                    time.sleep(0.5)
                else:
                    if random_num >= 75:
                        random_water = random.choice(['多喝熱水', '多喝冷水', '多喝冷水[emo5]', '多喝熱水[emo5]'])
                        self.plurk.callAPI('/APP/Responses/responseAdd', {
                        'plurk_id': pid,
                        'content': random_water,
                        'qualifier': ':'
                    })
                    time.sleep(0.5)
        except Exception as e:
            logging.error(f"回覆訊息發生錯誤: {e}")

    def process_messages(self, msgs):
        for msg in msgs:
            if msg.get('type') == 'new_plurk':
                pid = msg.get('plurk_id')
                user_id = msg.get('user_id')  # 取得 user_id
                content = msg.get('content_raw')
                qualifier = msg.get('qualifier')
                logging.info(f"{user_id} 新訊息: {qualifier} - {content}")
                self.respond_to_message(pid, user_id, content, qualifier)

    def run(self):
        while True:
            try:
                self.get_comet_channel()
                # logging.info("啟動 PlurkBot")
                self.plurk.callAPI('/APP/Alerts/addAllAsFriends')
                req = urllib.request.urlopen(self.comet_channel % self.new_offset, timeout=80)
                rawdata = req.read().decode('utf-8')
                match = self.jsonp_re.match(rawdata)
                if match:
                    rawdata = match.group(1)
                data = json.loads(rawdata)
                self.new_offset = data.get('new_offset', -1)
                msgs = data.get('data')
                if msgs:
                    self.process_messages(msgs)
            except Exception as e:
                logging.error(f"發生錯誤: {e}")