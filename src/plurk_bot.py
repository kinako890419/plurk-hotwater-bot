import logging
import re
import json
import time
import urllib.request


class PlurkBot:
    def __init__(self, plurk_api, content_response):
        self.plurk = plurk_api
        self.gemini_api = content_response
        self.comet_channel = None
        self.new_offset = -1
        self.jsonp_re = re.compile(r'CometChannel\.scriptCallback\((.+)\);\s*')
        logging.info("PlurkBot 初始化完成")

    def get_comet_channel(self):
        comet = self.plurk.callAPI('/APP/Realtime/getUserChannel')
        self.comet_channel = comet.get('comet_server') + "&new_offset=%d"
        logging.info("取得 Comet Channel")

    def respond_to_message(self, pid, content, qualifier):
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
                        'qualifier': 'thinks'
                    })
                    time.sleep(1)
            else:
                response = self.gemini_api.generate_response(content, 'default')
                logging.info(f"回覆內容: {response}")
                self.plurk.callAPI('/APP/Responses/responseAdd', {
                    'plurk_id': pid,
                    'content': response,
                    'qualifier': 'thinks'
                })
                time.sleep(0.5)
        except Exception as e:
            logging.error(f"回覆訊息發生錯誤: {e}")

    def process_messages(self, msgs):
        for msg in msgs:
            if msg.get('type') == 'new_plurk':
                pid = msg.get('plurk_id')
                content = msg.get('content_raw')
                qualifier = msg.get('qualifier')
                logging.info(f"新訊息: {qualifier} - {content}")
                self.respond_to_message(pid, content, qualifier)

    def run(self):
        self.get_comet_channel()
        logging.info("啟動 PlurkBot")
        while True:
            try:
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