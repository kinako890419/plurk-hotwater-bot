import google.generativeai as genai
import random
from get_random_tarot_info import get_random_tarot_info

class GenerateContentResponse:
    def __init__(self, api_key):
        genai.configure(api_key=api_key, transport='rest')
        self.model = genai.GenerativeModel("gemini-2.0-flash")

    def gemini_api_response(self, prompt):
        response = self.model.generate_content(prompt)
        return response.text

    def generate_prompt(self, cleaned_content, style='default'):
        if style == 'tarot':
            card_result, card_info_list = get_random_tarot_info()
            return f"""你是一位專精偉特塔羅占卜的大師級占卜師，使用經典的78張偉特牌(Rider-Waite-Smith Tarot)進行占卜。

當我提出問題後，會產生抽牌結果，使用三張牌陣進行解讀：
- 左方（過去）：*影響當前的過往*
- 中間（現在）：*當前面臨的核心議題*
- 右方（建議）：*未來可行的方向*

請依照以下格式回覆：
```
**你抽到的牌是：{card_result}**

---

請依序為每張牌提供：

**1. 內容分析**
- 牌名正逆位狀態
- 牌義與提問的直接連結（重點以**粗體**標示）
- 具體可行的建議（以bullet points呈現）

**2. 整體統整**
以三個段落分析：
2.1. 三張牌的關聯性與整體趨勢
2.2. 建議執行的時間點與行動方案
2.3. 需要特別注意的警訊

**3. 總結與建議**

這段可根據提問給出相關建議

```

請在500字內完成回覆，確保描述生動且易於理解。每個建議都需要具體可執行，避免模糊空泛的建議。重要關鍵字請使用**粗體**標示，補充說明使用*斜體*標示。
請將牌面資訊、內容分析與整體統整的內容各段落以`---`分隔(markdown line)，請注意每段以`---`分開的內容要在150字以內。

接下來我會提出我的問題，請直接給我問題的結果與回答： <{cleaned_content}>
請注意如果您判斷這不是個疑問，則根據您的判斷，從<{cleaned_content}>當中的關鍵字提供一個占卜結果。
不管回覆為何，請直接立即給我回覆，不必分成多段對話進行。
語言一律使用繁體中文。
"""
        elif style == 'bad_advice':
            bad_advices = ["說不定他其實很討厭你", "你不能自己處理一下嗎？",
                            "這有什麼好難過的？", "多喝熱水。"]
            bad_ans = random.choice(bad_advices)
            return f"""你是一個沒什麼同理心的男朋友，今天你的女朋友在跟你訴苦，
你的女朋友抱怨是：{cleaned_content}
你要用這個開頭來回覆他一句話：{bad_ans}
產生一句話，盡量讓他覺得你很不在乎，或者是你很不想聽他說話。
"""
        elif style == 'rap':

            return f"""用繁體中文回答我所有的問題。我的問題是：{cleaned_content}

你必須用以下所提供的格式回答，其中的<問題>填入的是與我的問題相關的主旨，<名詞>是與問題相關的詞。
注意：<問題>一定要是四個字，<名詞>一定要是兩個字，<你>可以依據你回答的內容做變化。

## 回答格式如下：
```
為什麼<你>不能<我的問題>
是因為
<你>在<問題>上面
<你>在<問題>上面
<你>在<問題>上面
<你>跟<名詞>唱反調：）
```
## 以下是範例：
我的問題是：朋友為什麼不能加薪？
## 範例回答如下：
為什麼朋友不能加薪
是因為
朋友在薪水問題上面
朋友在老闆情緒上面
朋友在工作處理上面
朋友跟公司唱反調：）
---
注意，請回傳你的回覆就好。
"""

        else:
            advices = ["好，", "好", "不要", "是喔，", "多喝熱水", "不知道", "不知道，", "不要，", "才不要，"]
            ans_start = random.choice(advices)
            return f"""根據下面內容，使用繁體中文，以【{ans_start}】為開頭隨便回我一句長度在\"20\"字以內的話: 
```
{cleaned_content}
```
"""

    def generate_response(self, cleaned_content, style):
        prompt = self.generate_prompt(cleaned_content, style)
        response = self.gemini_api_response(prompt)
        return response.split('---')
    
# if __name__ == "__main__":
#     test_res = GenerateContentResponse("")
#     response = test_res.generate_response("啊啊啊啊啊啊", "tarot")

#     for res in response:
#         print(res)