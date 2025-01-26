import re
import json
import time
import urllib.request
from plurk_oauth import PlurkAPI
from response_content import ContentResponse


class PlurkBot:
    def __init__(self, consumer_key, consumer_secret, token, token_secret, gemini_api_key):
        self.plurk = PlurkAPI(consumer_key, consumer_secret)
        self.plurk.authorize(token, token_secret)
        self.comet_channel = None
        self.new_offset = -1
        self.jsonp_re = re.compile(r'CometChannel\.scriptCallback\((.+)\);\s*')
        self.gemini_api = ContentResponse(gemini_api_key)

    def get_comet_channel(self):
        comet = self.plurk.callAPI('/APP/Realtime/getUserChannel')
        self.comet_channel = comet.get('comet_server') + "&new_offset=%d"

    def respond_to_message(self, pid, content, qualifier):
        try:
            if "！" in content:
                content = content.replace("！", "!")

            if (qualifier == 'hopes' or qualifier == 'wishes') and '!抽' in content: # 希望
                print(content)

                cleaned_content = content.replace(' ', '').replace('!抽', '')
                print(cleaned_content)
                response_parts = self.gemini_api.generate_response(cleaned_content, 'tarot')
                for part in response_parts:
                    print(part)
                    self.plurk.callAPI('/APP/Responses/responseAdd', {
                        'plurk_id': pid,
                        'content': part.strip(),
                        'qualifier': 'thinks'
                    })
                    time.sleep(1)
            elif qualifier == 'wants' and '!抱怨' in content: # 想要
                print(content)
                # 剃除 content 中的空白和 !抱怨 關鍵字
                cleaned_content = content.replace(' ', '').replace('!抱怨', '')
                print(cleaned_content)
                response_parts = self.gemini_api.generate_response(cleaned_content, 'bad_advice')
                for part in response_parts:
                    print(part)
                    self.plurk.callAPI('/APP/Responses/responseAdd', {
                        'plurk_id': pid,
                        'content': part.strip(),
                        'qualifier': 'thinks'
                    })
                    time.sleep(1)
            elif qualifier == 'asks' and '!為什麼' in content: # 問
                print(content)
                cleaned_content = content.replace(' ', '').replace('!為什麼', '')
                print(cleaned_content)
                response_parts = self.gemini_api.generate_response(cleaned_content, 'rap')
                for part in response_parts:
                    print(part)
                    self.plurk.callAPI('/APP/Responses/responseAdd', {
                        'plurk_id': pid,
                        'content': part.strip(),
                        'qualifier': 'thinks'
                    })
                    time.sleep(1)
        except Exception as e:
            print(f"回覆訊息發生錯誤: {e}")

    def process_messages(self, msgs):
        for msg in msgs:
            if msg.get('type') == 'new_plurk':
                pid = msg.get('plurk_id')
                content = msg.get('content_raw')
                qualifier = msg.get('qualifier')
                print(qualifier, content)
                self.respond_to_message(pid, content, qualifier)

    def run(self):
        self.get_comet_channel()
        print("Starting bot")
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
                print(f"發生錯誤: {e}")