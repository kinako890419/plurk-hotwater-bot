import google.generativeai as genai
import random


class ContentResponse:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def gemini_api_response(self, prompt):
        response = self.model.generate_content(prompt)
        return response.text

    def generate_prompt(self, cleaned_content, style):
        if style == 'tarot':
            return f"""你是一位專精偉特塔羅占卜的大師級占卜師，使用經典的78張偉特牌(Rider-Waite-Smith Tarot)進行占卜。

當我提出問題後，會產生抽牌結果，使用三張牌陣進行解讀：
- 左方（過去）：*影響當前的過往*
- 中間（現在）：*當前面臨的核心議題*
- 右方（建議）：*未來可行的方向*

請依照以下格式回覆：

**你抽到的牌是：<三張牌面結果做為標題>**

請依序為每張牌提供：
1. **牌面資訊**
- 牌名與編號(大阿爾卡納標註0-21)
- 正逆位狀態
- 3個關鍵字詮釋（以*斜體*標示）

2. **內容分析**
- 牌義與提問的直接連結（重點以**粗體**標示）
- 具體可行的建議（以bullet points呈現）

**整體統整**
以三個段落分析：
1. 三張牌的關聯性與整體趨勢
2. 建議執行的時間點與行動方案
3. 需要特別注意的警訊

請在500字內完成回覆，確保描述生動且易於理解。每個建議都需要具體可執行，避免模糊空泛的建議。重要關鍵字請使用**粗體**標示，補充說明使用*斜體*標示。
請將牌面資訊、內容分析與整體統整的內容各段落以`---`分隔，請注意每段以`---`分開的內容要在150字以內。

接下來我會提出我的問題，請直接給我問題的結果與回答： <{cleaned_content}>
請注意如果您判斷這不是個疑問，則根據您的判斷，從<{cleaned_content}>當中的關鍵字提供一個占卜結果。
不管回覆為何，請直接立即給我回覆，不必分成多段對話進行。
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
            return f"根據下面內容隨便回我一句話: {cleaned_content}"

    def generate_response(self, cleaned_content, style):
        prompt = self.generate_prompt(cleaned_content, style)
        response = self.gemini_api_response(prompt)
        return response.split('---')