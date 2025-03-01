import json
import random


def get_random_tarot_info():
    # 讀取JSON檔案
    with open('tarot_zhtw.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    # 隨機選擇三張牌
    card_ids = random.sample(range(0, 78), 3)
    card_info_list = []
    card_result = []
    card_name = []

    for card_id in card_ids:
        if card_id == 0:
            card_id_str = '00'
        elif card_id < 10:
            card_id_str = '0' + str(card_id)
        else:
            card_id_str = str(card_id)

        positive_negative = random.randint(0, 1)

        card = data[card_id_str]['explain']
        card_pos_neg = data[card_id_str]['positive'] if positive_negative == 1 else data[card_id_str]['reversed']

        card_result.append(data[card_id_str]['name'])

        card_name.append(f"{data[card_id_str]['name']}，{card_pos_neg}")

        card_info = f"卡片名稱：{card_name}\n卡片解釋：{card}\n行為：{card_pos_neg['behavior']}\n愛情：{card_pos_neg['marriage']}\n意義：{card_pos_neg['meaning']}\n相關詞：{card_pos_neg['related']}\n兩性關係：{card_pos_neg['sexuality']}\n星座：{card_pos_neg['star']}"
        card_info_list.append(card_info)

    return card_result, "\n\n".join(card_info_list)


if __name__ == "__main__":
    card_result, card_info_list = get_random_tarot_info()
    print(card_result)
    # print(card_info)
    # print(card_info_list)
    # print("\n".join(tarot_info[1]))