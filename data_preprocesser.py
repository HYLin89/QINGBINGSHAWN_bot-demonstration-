import json
import pandas as pd
import os,sys
import re

def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller 打包後的暫存路徑
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, relative_path)

mapping_rules={
    'apple':['蘋果'],
    'asparagus':['蘆筍','青菜','蔬菜'],
    'avocado':['酪梨','牛油果'],
    'banana':['香蕉'],
    'bell pepper':['青椒','紅椒','黃椒','彩椒','甜椒'],
    'bitter gourd':['苦瓜'],
    'bok choy':['小白菜','青江菜','小松菜','菜葉','青菜','蔬菜','葉菜'],
    'broccoli':['青花菜','花椰菜','綠花椰菜','青花椰菜','蔬菜'],
    'cabbage':['美生菜','萵苣','空心菜','高麗菜','蔬菜','葉菜'],
    'carrot':['蘿蔔','红萝卜'],
    'cashew':['腰果','堅果'],
    'cauliflower':['白花椰菜','花椰菜','蔬菜'],
    'chayote':['瓠瓜','佛手瓜'],
    'chicken breast':['雞胸','雞柳','雞肉','雞里肌','烤雞','白斬雞','炸雞'],
    'chicken thigh':['雞腿','烤雞','白斬雞','炸雞'],
    'chicken wing':['雞翅','烤雞','白斬雞','炸雞'],
    'chilli':['辣椒','糯米椒','燈籠椒','花椒'],
    'coconut':['椰子'],
    'coconuts':['椰子'],
    'corn':['玉米'],
    'crab':['蟹'],
    'crust':['餅皮','餃皮','春捲皮','春卷皮','餛飩皮'],
    'cucumber':['黃瓜'],
    'dried tofu':['豆干','豆乾','豆皮','豆包'],
    'egg':['蛋'],
    'egg_':['蛋'],
    'eggplant':['茄子'],
    'fish':['魚'],
    'garlic':['蒜'],
    'ginger':['薑'],
    'grapes':['葡萄'],
    'lemon':['檸檬','萊姆'],
    'lettuce':['白菜','娃娃菜','生菜','青菜','蔬菜','葉菜'],
    'lobster tails':['龍蝦'],
    'mango':['芒果'],
    'melon':['蜜瓜'],
    'milk':['牛奶','鮮奶'],
    'mince':['絞肉','攪肉'],
    'okra':['秋葵'],
    'onion':['洋蔥'],
    'orange':['柳橙','橘子','甜橙'],
    'oysters':['牡蠣'],
    'papaya':['木瓜'],
    'peanuts':['花生'],
    'peas':['豆'],
    'peper':['辣椒','糯米椒','燈籠椒','花椒'],
    'pepper':['辣椒','糯米椒','燈籠椒','花椒'],
    'pineapple':['鳳梨'],
    'pork belly':['豬'],
    'potato':['馬鈴薯','土豆'],
    'pumpkin':['南瓜'],
    'radishes':['甜菜根'],
    'red rice':['紅米'],
    'salmon':['鮭魚'],
    'sea scallops':['貝'],
    'shrimp':['蝦'],
    'spinach':['菠菜','油菜','青菜','蔬菜'],
    'strawberry':['草莓'],
    'sweet potato':['地瓜','番薯'],
    'tempeh':[],
    'tofu':['豆腐'],
    'tomato':['番茄'],
    'tuna':['鮪魚'],
    'white rice':['飯','米'],
    'zuccini':['櫛瓜']
}


exclusion_rules={
    'apple':[],
    'asparagus':[],
    'avocado':['油'],
    'banana':[],
    'bell pepper':['粉'],
    'bitter gourd':[],
    'bok choy':[],
    'broccoli':[],
    'cabbage':[],
    'carrot':['白'],
    'cashew':[],
    'cauliflower':[],
    'chayote':[],
    'chicken breast':['香料'],
    'chicken thigh':[],
    'chicken wing':[],
    'chilli':['油','粉','粒'],
    'coconut':['油'],
    'coconuts':['油'],
    'corn':['粉','筍'],
    'crab':[],
    'crust':[],
    'cucumber':[],
    'dried tofu':[],
    'egg':['粉','餅','糕','豆腐','麵','面','餃'],
    'egg_':['粉','餅','糕','豆腐','麵','面','餃'],
    'eggplant':['醬'],
    'fish':['小魚','魚露','魷魚','烏魚子','柴魚','章魚','油','粉','丸','鯷魚','曼波魚','魚漿','魚板','罐'],
    'garlic':['油','苗','青','味'],
    'ginger':['粉'],
    'grapes':['油','乾','干'],
    'lemon':[],
    'lettuce':['美生菜'],
    'lobster tails':[],
    'mango':[],
    'melon':[],
    'milk':['奶油','粉'],
    'mince':[],
    'okra':[],
    'onion':[],
    'orange':[],
    'oysters':[],
    'papaya':['青'],
    'peanuts':['油','糖'],
    'peas':['紅','豆芽','豆瓣醬','豆輪','豆薯','豆沙','醬油','豆蔻','荳蔻','豆鼓','豆干','豆乾','豆皮','豆包','豆腐'],
    'peper':['油','粉','粒'],
    'pepper':['油','粉','粒'],
    'pineapple':[],
    'pork belly':['絞肉','攪肉','油','醬','血'],
    'potato':[],
    'pumpkin':['子','仔'],
    'radishes':[],
    'red rice':[],
    'salmon':['油'],
    'sea scallops':['醬','貝殼'],
    'shrimp':['漿','蝦夷','龍蝦','櫻花蝦','丸','米','餃'],
    'spinach':[],
    'strawberry':[],
    'sweet potato':['粉','葉'],
    'tempeh':[],
    'tofu':['乳'],
    'tomato':['醬','乾','罐','糊'],
    'tuna':['罐頭'],
    'white rice':['玉米','玄米','酒','油','蝦','花生','米香','糯米椒','米線','糕','血','醋','蒜','米粒狀','粉'],
    'zuccini':[]
}

def process_recipes(file_path):
    print("正在讀取資料...")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("錯誤：找不到 recipes.json 檔案")
        return

    # 初始化反向索引 (Inverted Index)
    inverted_index = {tag: [] for tag in mapping_rules.keys()}

    # 遍歷每一份食譜
    for recipe in data:
        recipe_id = recipe['ID']
        
        raw_ingredients_str = recipe['食材']
        
        ingredient_list=raw_ingredients_str.split('、')

        matched_tags = set()
        
        for raw_item in ingredient_list:
            for tag, keywords in mapping_rules.items():

                is_included = False
                for kw in keywords:
                    if kw in raw_item:
                        is_included = True
                        break
                
                if not is_included:
                    continue 
                
                should_exclude = False
                if tag in exclusion_rules:
                    for ex_kw in exclusion_rules[tag]:
                        if ex_kw in raw_item:
                            should_exclude = True
                            break
                
                if not should_exclude:
                    matched_tags.add(tag)
                    # print(f" 食材:'{raw_item}' -> 標籤:'{tag}'")

        recipe['yolo_tags'] = list(matched_tags)
        
        for tag in matched_tags:
            inverted_index[tag].append(recipe_id)

    # --- 3. 輸出結果與測試 ---
    
    print("\n【前 5 筆食譜處理結果範例】：")
    for i, recipe in enumerate(data[:5]):
        print(f"ID: {recipe.get('id')} | 菜名: {recipe.get('name')}")
        print(f"  原始食材: {recipe.get('ingredients_raw')}")
        print(f"  辨識標籤: {recipe.get('yolo_tags')}")
        print("-" * 30)

    print("\n【標籤統計 (部分)】：")
    count = 0
    for tag, ids in inverted_index.items():
        if len(ids) > 0:
            print(f"  {tag}: {len(ids)} 筆食譜")
            count += 1
            if count >= 10: # 只列出前10個有資料的標籤
                print("  ... (更多標籤隱藏)")
                break

    output_file = 'recipes_tagged.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    index_file = 'inverted_index.json'
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(inverted_index, f, ensure_ascii=False, indent=4)

    print(f"\nALL DONE！\n已生成 '{output_file}' (含標籤的食譜) \n已生成 '{index_file}' (反向搜尋索引)")

  
if __name__ == "__main__":
    process_recipes('recipes.json')
        

    








