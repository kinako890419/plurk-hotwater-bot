import unittest
from unittest.mock import MagicMock, patch
from src.plurk_response import PlurkResponse

# FILE: plurk-hotwater-bot/tests/test_plurk_response.py
# 測試 process_messages function 是否能處理不同類型的訊息，檢查 respond_to_message 在符合特定條件時是否能被正確調用
# python -m unittest discover -s tests -v

class TestPlurkResponse(unittest.TestCase):
    def setUp(self):
        self.mock_plurk_api = MagicMock()
        self.mock_content_response = MagicMock()
        self.plurk_response = PlurkResponse(self.mock_plurk_api, self.mock_content_response)

    def test_process_messages_new_plurk(self):
        test_cases = [
            {
                'type': 'new_plurk',
                'plurk_id': 12345,
                'content_raw': 'Test content !抽',
                'qualifier': 'hopes',
                'response': ['抽牌回應 part1', '抽牌回應 part2'],
                'expected_calls': [
                    ('/APP/Responses/responseAdd', {
                        'plurk_id': 12345,
                        'content': '抽牌回應 part1',
                        'qualifier': 'thinks'
                    }),
                    ('/APP/Responses/responseAdd', {
                        'plurk_id': 12345,
                        'content': '抽牌回應 part2',
                        'qualifier': 'thinks'
                    })
                ],
                'response_type': 'tarot'
            },
            {
                'type': 'new_plurk',
                'plurk_id': 12346,
                'content_raw': 'Test content !抱怨',
                'qualifier': 'wants',
                'response': ['抱怨建議'],
                'expected_calls': [
                    ('/APP/Responses/responseAdd', {
                        'plurk_id': 12346,
                        'content': '抱怨建議',
                        'qualifier': 'thinks'
                    })
                ],
                'response_type': 'bad_advice'
            },
            {
                'type': 'new_plurk',
                'plurk_id': 12347,
                'content_raw': 'Test content !為什麼',
                'qualifier': 'asks',
                'response': ['饒舌回應'],
                'expected_calls': [
                    ('/APP/Responses/responseAdd', {
                        'plurk_id': 12347,
                        'content': '饒舌回應',
                        'qualifier': 'feels'
                    })
                ],
                'response_type': 'rap'
            },
            {
                'type': 'new_plurk',
                'plurk_id': 12348,
                'content_raw': 'Test content 機器人',
                'qualifier': 'says',
                'response': ['機器人回應'],
                'expected_calls': [
                    ('/APP/Responses/responseAdd', {
                        'plurk_id': 12348,
                        'content': '機器人回應',
                        'qualifier': ':'
                    })
                ],
                'response_type': 'default'
            }
        ]

        for case in test_cases:
            with self.subTest(case=case):
                
                self.mock_plurk_api.reset_mock()
                self.mock_content_response.reset_mock()
                
                # 設置 mock 回應
                self.mock_content_response.generate_response.return_value = case['response']
                
                # 執行測試
                self.plurk_response.process_messages([case])
                
                # 驗證 generate_response 被正確調用
                cleaned_content = case['content_raw'].replace(' ', '')
                if case['response_type'] in ['tarot', 'bad_advice', 'rap']:
                    cleaned_content = cleaned_content.replace(
                        {'tarot': '!抽', 'bad_advice': '!抱怨', 'rap': '!為什麼'}[case['response_type']], 
                        ''
                    )
                self.mock_content_response.generate_response.assert_called_with(
                    cleaned_content, 
                    case['response_type']
                )
                
                # 驗證每個預期的 API 調用
                self.assertEqual(
                    len(case['expected_calls']),
                    self.mock_plurk_api.callAPI.call_count,
                    f"預期的 API 調用次數不符合：{len(case['expected_calls'])} != {self.mock_plurk_api.callAPI.call_count}"
                )
                
                for i, expected_call in enumerate(case['expected_calls']):
                    actual_call = self.mock_plurk_api.callAPI.call_args_list[i]
                    self.assertEqual(
                        expected_call,
                        actual_call.args,
                        f"第 {i+1} 次 API 調用參數不符合預期"
                    )

    def test_process_messages_random_responses(self):
        test_cases = [
            {
                'type': 'new_plurk',
                'plurk_id': 12349,
                'content_raw': 'Test content 好不好',
                'qualifier': 'asks',
                'expected_responses': ['好', '不要', '[emo3]', '[emo4]'],
                'expected_qualifier': 'feels'
            },
            {
                'type': 'new_plurk',
                'plurk_id': 12350,
                'content_raw': 'Test content 熱水',
                'qualifier': 'asks',
                'expected_response': '多喝熱水',
                'expected_qualifier': 'says'
            }
        ]

        for case in test_cases:
            with self.subTest(case=case):
                
                self.mock_plurk_api.reset_mock()
                
                # 執行測試
                self.plurk_response.process_messages([case])
                
                # 驗證 API 調用
                self.mock_plurk_api.callAPI.assert_called_once()
                actual_call = self.mock_plurk_api.callAPI.call_args
                
                if 'expected_responses' in case:
                    # 對於隨機回應，確認回應在預期的選項中
                    self.assertIn(
                        actual_call.args[1]['content'],
                        case['expected_responses'],
                        "隨機回應不在預期的選項中"
                    )
                else:
                    # 對於固定回應，直接比對
                    self.assertEqual(
                        actual_call.args[1]['content'],
                        case['expected_response'],
                        "固定回應不符合預期"
                    )
                
                # 驗證其他參數
                self.assertEqual(
                    actual_call.args[0],
                    '/APP/Responses/responseAdd',
                    "API 端點不符合預期"
                )
                self.assertEqual(
                    actual_call.args[1]['plurk_id'],
                    case['plurk_id'],
                    "plurk_id 不符合預期"
                )
                self.assertEqual(
                    actual_call.args[1]['qualifier'],
                    case['expected_qualifier'],
                    "qualifier 不符合預期"
                )

    def test_process_messages_non_new_plurk(self):
        msgs = [
            {
                'type': 'non_new_plurk',
                'plurk_id': 12345,
                'content_raw': 'Test content',
                'qualifier': 'hopes'
            }
        ]
        
        # 執行測試
        self.plurk_response.process_messages(msgs)
        
        # 驗證沒有進行任何 API 調用
        self.mock_plurk_api.callAPI.assert_not_called()

    @patch('random.randint')
    def test_random_response_probability(self, mock_randint):
        
        mock_randint.return_value = 5
        msg = {
            'type': 'new_plurk',
            'plurk_id': 12351,
            'content_raw': 'Test content',
            'qualifier': 'says'
        }
        
        self.mock_content_response.generate_response.return_value = ['random response']
        self.plurk_response.process_messages([msg])
        
        self.mock_content_response.generate_response.assert_called_once()
        self.mock_plurk_api.callAPI.assert_called_once()

        mock_randint.return_value = 95
        self.mock_plurk_api.reset_mock()
        self.mock_content_response.reset_mock()
        
        self.plurk_response.process_messages([msg])
        
        self.mock_plurk_api.callAPI.assert_called_once()
        actual_call = self.mock_plurk_api.callAPI.call_args
        self.assertIn(
            actual_call.args[1]['content'],
            ['多喝熱水', '多喝冷水', '多喝冷水[emo5]', '多喝熱水[emo5]'],
            "隨機水回應不在預期的選項中"
        )

if __name__ == '__main__':
    unittest.main()