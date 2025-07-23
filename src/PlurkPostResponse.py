import logging
import re
import json
import threading
import time
import urllib.request
import random
import os

import schedule

class PlurkPostResponse:
    """
    抓取 Plurk 的 Comet Channel 並回覆訊息
    這個class會持續運行，並在有新 Plurk 訊息時進行回覆
    """
    def __init__(self, plurk_api, content_response):
        self.plurk = plurk_api
        self.gemini_response = content_response
        self.comet_channel = None
        self.new_offset = -1
        self.jsonp_re = re.compile(r'CometChannel\.scriptCallback\((.+)\);\s*')
        self.user_status = []
        logging.info("PlurkBot 初始化完成")
        schedule.every().day.at("00:00").do(self._clear_user_status)
        threading.Thread(target=self._run_schedule, daemon=True).start()
        # 讀取每日運勢 JSON
        fortune_path = os.path.join(os.path.dirname(__file__), 'daily_fortune.json')
        try:
            with open(fortune_path, 'r', encoding='utf-8') as f:
                self.daily_fortune_list = json.load(f)
            logging.info("已載入每日運勢 JSON")
        except Exception as e:
            logging.error(f"載入每日運勢 JSON 失敗: {e}")
            self.daily_fortune_list = [
                "不好吧",
                "今天還行",
                "今天宜多喝水",
                "今天宜多喝熱水",
                "今天宜多喝冷水",
                "今天宜多喝冰水",
                "今天宜多喝熱茶",
            ]

    def run(self):
        while True:
            try:
                self._get_comet_channel()
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
                    self._process_messages(msgs)
            except Exception as e:
                logging.error(f"發生錯誤: {e}")

    def _clear_user_status(self):
        self.user_status.clear()
        logging.info("清空 user_status")

    def _get_current_user_id(self):
        """取得當前使用者 ID"""
        try:
            user_info = self.plurk.callAPI('/APP/Users/me')
            return user_info.get('id')
        except Exception as e:
            logging.error(f"無法取得當前使用者 ID: {e}")
            return None

    def _is_friend(self, user_id):
        """檢查使用者是否為好友"""
        try:
            logging.info(f"檢查 {user_id} 是否為好友...")
            
            # 取得當前使用者 ID
            current_user_id = self._get_current_user_id()
            if not current_user_id:
                return False
            
            friends_data = []
            offset = 0
            
            # 分批取得所有好友
            while True:
                batch = self.plurk.callAPI('/APP/FriendsFans/getFriendsByOffset', {
                    'user_id': current_user_id,
                    'offset': offset,
                    'limit': 100
                })
                
                if not batch or len(batch) == 0:
                    break
                    
                friends_data.extend(batch)
                offset += 100
                
                if len(batch) < 100:  # 如果回傳數量少於限制，表示已到最後一頁
                    break
            
            # 檢查是否在好友列表中
            friend_ids = {friend['id'] for friend in friends_data}
            friend_list = user_id in friend_ids

            return friend_list
            
        except Exception as e:
            logging.error(f"檢查好友狀態時發生錯誤: {e}")
            return False 

    def _run_schedule(self):
        while True:
            schedule.run_pending()
            time.sleep(1)
    
    def _get_comet_channel(self):
        comet = self.plurk.callAPI('/APP/Realtime/getUserChannel')
        self.comet_channel = comet.get('comet_server') + "&new_offset=%d"
        logging.info("取得 Comet Channel")

    def _respond_to_message(self, pid, user_id, owner_id, content, qualifier):
        try:
            # 檢查發文者是否為好友
            if not self._is_friend(owner_id):
                logging.info(f"跳過非好友 {owner_id} 的訊息")
                return
                
            if "！" in content:
                content = content.replace("！", "!")
            logging.info(f"處理訊息: {content} (qualifier: {qualifier})")

            if (qualifier == 'hopes' or qualifier == 'wishes') and '!抽' in content: # 希望
                cleaned_content = content.replace(' ', '').replace('!抽', '')
                logging.info(f"清理後的內容: {cleaned_content}")
                response_parts = self.gemini_response.generate_response(cleaned_content, 'tarot')
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
                response_parts = self.gemini_response.generate_response(cleaned_content, 'bad_advice')
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
                response_parts = self.gemini_response.generate_response(cleaned_content, 'rap')
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
                    'content': random.choice(self.daily_fortune_list),
                    'qualifier': 'thinks'
                })
                time.sleep(1)
            elif qualifier == 'asks' and '!要不要' in content:
                cleaned_content = content.replace(' ', '').replace('!要不要', '')
                logging.info(f"清理後的內容: {cleaned_content}")
                response = self.gemini_response.generate_response(cleaned_content, 'choose')
                if response:
                    self.plurk.callAPI('/APP/Responses/responseAdd', {
                        'plurk_id': pid,
                        'content': response,
                        'qualifier': 'feels'
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

    def _process_messages(self, msgs):
        for msg in msgs:
            if (msg.get('type') == 'new_plurk') and (msg.get('plurk_type') == 0):
                pid = msg.get('plurk_id')
                user_id = msg.get('user_id')  # 噗文所屬的時間軸 ID
                owner_id = msg.get('owner_id')  # 噗文的原始發文者 ID
                content = msg.get('content_raw')
                qualifier = msg.get('qualifier')
                logging.info(f"{owner_id} 新訊息: {qualifier} - {content}")
                self._respond_to_message(pid, user_id, owner_id, content, qualifier)
            else:
                continue
