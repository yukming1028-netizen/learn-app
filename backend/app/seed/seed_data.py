"""Seed data: 60 questions across grades 1-3, 4 subjects."""
from app.models.question import Question

QUESTIONS = [
    # === Grade 1 Math (小一數學) ===
    {"subject": "math", "grade": 1, "difficulty": 1, "type": "choice", "content": "5 + 3 = ?", "options": ["6", "7", "8", "9"], "answer": "8", "explanation": "5個加上3個等於8個", "tags": ["加法", "個位數"]},
    {"subject": "math", "grade": 1, "difficulty": 1, "type": "choice", "content": "7 - 2 = ?", "options": ["4", "5", "6", "3"], "answer": "5", "explanation": "7個減去2個等於5個", "tags": ["減法", "個位數"]},
    {"subject": "math", "grade": 1, "difficulty": 2, "type": "choice", "content": "9 + 6 = ?", "options": ["14", "15", "16", "13"], "answer": "15", "explanation": "9+6=15，需要進位", "tags": ["加法", "進位"]},
    {"subject": "math", "grade": 1, "difficulty": 2, "type": "choice", "content": "12 - 5 = ?", "options": ["6", "7", "8", "5"], "answer": "7", "explanation": "12-5=7，需要退位", "tags": ["減法", "退位"]},
    {"subject": "math", "grade": 1, "difficulty": 1, "type": "choice", "content": "哪個數字最大？", "options": ["3", "7", "5", "1"], "answer": "7", "explanation": "7比3、5、1都大", "tags": ["比較大小"]},
    {"subject": "math", "grade": 1, "difficulty": 3, "type": "choice", "content": "8 + 7 + 3 = ?", "options": ["16", "17", "18", "19"], "answer": "18", "explanation": "8+7=15，15+3=18", "tags": ["連加"]},
    {"subject": "math", "grade": 1, "difficulty": 2, "type": "input", "content": "15 + 10 = ?", "answer": "25", "explanation": "15加10等於25", "tags": ["加法", "兩位數"]},
    {"subject": "math", "grade": 1, "difficulty": 1, "type": "choice", "content": "數一數，🟥🟥🟥🟥有幾個？", "options": ["3", "4", "5", "6"], "answer": "4", "explanation": "共有4個紅色方塊", "tags": ["數數"]},

    # === Grade 1 Chinese (小一語文) ===
    {"subject": "chinese", "grade": 1, "difficulty": 1, "type": "choice", "content": "「日」字有幾畫？", "options": ["3畫", "4畫", "5畫", "6畫"], "answer": "4畫", "explanation": "日字共有4畫：豎、橫折、橫、橫", "tags": ["筆畫"]},
    {"subject": "chinese", "grade": 1, "difficulty": 1, "type": "choice", "content": "下列哪個是「大」的反義詞？", "options": ["多", "小", "高", "長"], "answer": "小", "explanation": "大和小是反義詞", "tags": ["反義詞"]},
    {"subject": "chinese", "grade": 1, "difficulty": 2, "type": "choice", "content": "「木」加一畫變成什麼字？", "options": ["本", "禾", "以上都是", "都不是"], "answer": "以上都是", "explanation": "木加一橫成「本」，加一撇成「禾」", "tags": ["字形"]},
    {"subject": "chinese", "grade": 1, "difficulty": 2, "type": "choice", "content": "「天」的注音是？", "options": ["ㄊㄧㄢ", "ㄉㄚˋ", "ㄕㄢ", "ㄇㄧㄢˊ"], "answer": "ㄊㄧㄢ", "explanation": "天的注音是ㄊㄧㄢ（一聲）", "tags": ["注音"]},
    {"subject": "chinese", "grade": 1, "difficulty": 1, "type": "choice", "content": "哪個字讀作「ㄇㄚ」？", "options": ["爸", "媽", "馬", "以上都是"], "answer": "以上都是", "explanation": "爸、媽、馬都有ㄇㄚ的音", "tags": ["注音"]},

    # === Grade 1 English (小一英語) ===
    {"subject": "english", "grade": 1, "difficulty": 1, "type": "choice", "content": "What color is the sun? ☀️", "options": ["Red", "Yellow", "Blue", "Green"], "answer": "Yellow", "explanation": "The sun is yellow!", "tags": ["colors"]},
    {"subject": "english", "grade": 1, "difficulty": 1, "type": "choice", "content": "How many is \"three\"?", "options": ["2", "3", "4", "5"], "answer": "3", "explanation": "Three means 3 (三)", "tags": ["numbers"]},
    {"subject": "english", "grade": 1, "difficulty": 1, "type": "choice", "content": "Which animal says \"Woof\"?", "options": ["Cat", "Dog", "Bird", "Fish"], "answer": "Dog", "explanation": "A dog says woof! 🐶", "tags": ["animals"]},
    {"subject": "english", "grade": 1, "difficulty": 2, "type": "choice", "content": "What is \"蘋果\" in English?", "options": ["Banana", "Apple", "Orange", "Grape"], "answer": "Apple", "explanation": "蘋果 = Apple 🍎", "tags": ["fruits", "vocabulary"]},
    {"subject": "english", "grade": 1, "difficulty": 2, "type": "choice", "content": "Good morning! How do you reply?", "options": ["Good night", "Good morning!", "Goodbye", "Thank you"], "answer": "Good morning!", "explanation": "Reply with the same greeting!", "tags": ["greetings"]},

    # === Grade 1 Science (小一科學) ===
    {"subject": "science", "grade": 1, "difficulty": 1, "type": "choice", "content": "植物需要什麼來生長？", "options": ["陽光和水", "黑暗", "寒冷", "噪音"], "answer": "陽光和水", "explanation": "植物需要陽光和水才能生長🌱", "tags": ["植物"]},
    {"subject": "science", "grade": 1, "difficulty": 1, "type": "choice", "content": "太陽從哪個方向升起？", "options": ["東邊", "西邊", "北邊", "南邊"], "answer": "東邊", "explanation": "太陽從東邊升起，西邊落下", "tags": ["自然"]},
    {"subject": "science", "grade": 1, "difficulty": 2, "type": "choice", "content": "下列哪個是動物？", "options": ["石頭", "花朵", "小狗", "雲朵"], "answer": "小狗", "explanation": "小狗是動物，會動、需要吃東西", "tags": ["動物分類"]},
    {"subject": "science", "grade": 1, "difficulty": 2, "type": "choice", "content": "天空為什麼是藍色的？", "options": ["因為海水", "陽光散射", "因為藍色顏料", "不知道"], "answer": "陽光散射", "explanation": "陽光穿過大氣層時藍光散射最多", "tags": ["自然現象"]},

    # === Grade 2 Math (小二數學) ===
    {"subject": "math", "grade": 2, "difficulty": 1, "type": "choice", "content": "25 + 13 = ?", "options": ["35", "38", "37", "39"], "answer": "38", "explanation": "25+13=38", "tags": ["加法", "兩位數"]},
    {"subject": "math", "grade": 2, "difficulty": 2, "type": "choice", "content": "6 × 3 = ?", "options": ["16", "18", "20", "24"], "answer": "18", "explanation": "6乘以3等於18", "tags": ["乘法"]},
    {"subject": "math", "grade": 2, "difficulty": 2, "type": "choice", "content": "45 - 28 = ?", "options": ["15", "16", "17", "18"], "answer": "17", "explanation": "45-28=17", "tags": ["減法", "退位"]},
    {"subject": "math", "grade": 2, "difficulty": 3, "type": "choice", "content": "7 × 8 = ?", "options": ["54", "56", "58", "64"], "answer": "56", "explanation": "七八五十六", "tags": ["乘法", "九九乘法"]},
    {"subject": "math", "grade": 2, "difficulty": 1, "type": "choice", "content": "一打鉛筆有幾支？", "options": ["10", "12", "15", "20"], "answer": "12", "explanation": "一打 = 12", "tags": ["應用題"]},
    {"subject": "math", "grade": 2, "difficulty": 3, "type": "choice", "content": "小明有50元，買了文具花了23元，還剩多少？", "options": ["25元", "27元", "30元", "33元"], "answer": "27元", "explanation": "50-23=27", "tags": ["應用題", "減法"]},
    {"subject": "math", "grade": 2, "difficulty": 4, "type": "input", "content": "36 ÷ 4 = ?", "answer": "9", "explanation": "36除以4等於9", "tags": ["除法"]},
    {"subject": "math", "grade": 2, "difficulty": 2, "type": "choice", "content": "下列哪個是奇數？", "options": ["12", "14", "15", "16"], "answer": "15", "explanation": "15不能被2整除，是奇數", "tags": ["奇偶數"]},

    # === Grade 2 Chinese (小二語文) ===
    {"subject": "chinese", "grade": 2, "difficulty": 1, "type": "choice", "content": "「快樂」的近義詞是？", "options": ["傷心", "高興", "生氣", "害怕"], "answer": "高興", "explanation": "快樂和高興意思相近", "tags": ["近義詞"]},
    {"subject": "chinese", "grade": 2, "difficulty": 2, "type": "choice", "content": "「美麗」的反義詞是？", "options": ["漂亮", "醜陋", "好看", "可愛"], "answer": "醜陋", "explanation": "美麗和醜陋是反義詞", "tags": ["反義詞"]},
    {"subject": "chinese", "grade": 2, "difficulty": 2, "type": "choice", "content": "下列哪個詞語是形容詞？", "options": ["跑步", "藍色", "吃飯", "學校"], "answer": "藍色", "explanation": "藍色是形容顏色的詞", "tags": ["詞性"]},
    {"subject": "chinese", "grade": 2, "difficulty": 3, "type": "choice", "content": "「風和日麗」是什麼意思？", "options": ["天氣惡劣", "天氣晴朗溫和", "刮大風", "下大雨"], "answer": "天氣晴朗溫和", "explanation": "風和日麗形容天氣晴朗、微風和煦", "tags": ["成語"]},
    {"subject": "chinese", "grade": 2, "difficulty": 1, "type": "choice", "content": "「書」是什麼部首？", "options": ["曰部", "聿部", "曰/聿", "禾部"], "answer": "曰/聿", "explanation": "書的部首是曰部（或聿部）", "tags": ["部首"]},

    # === Grade 2 English (小二英語) ===
    {"subject": "english", "grade": 2, "difficulty": 2, "type": "choice", "content": "What day comes after Monday?", "options": ["Sunday", "Tuesday", "Friday", "Saturday"], "answer": "Tuesday", "explanation": "Monday → Tuesday (星期二)", "tags": ["days"]},
    {"subject": "english", "grade": 2, "difficulty": 1, "type": "choice", "content": "What is \"貓\" in English?", "options": ["Dog", "Cat", "Bird", "Fish"], "answer": "Cat", "explanation": "貓 = Cat 🐱", "tags": ["animals", "vocabulary"]},
    {"subject": "english", "grade": 2, "difficulty": 2, "type": "choice", "content": "Choose the correct sentence:", "options": ["I am a student.", "I a student am.", "Am I a student.", "Student I am a."], "answer": "I am a student.", "explanation": "Subject + verb + article + noun", "tags": ["grammar", "sentence"]},
    {"subject": "english", "grade": 2, "difficulty": 3, "type": "choice", "content": "What's the plural of \"child\"?", "options": ["childs", "children", "childes", "child"], "answer": "children", "explanation": "child → children (不規則複數)", "tags": ["plural", "grammar"]},
    {"subject": "english", "grade": 2, "difficulty": 1, "type": "choice", "content": "How do you say \"謝謝\"?", "options": ["Sorry", "Thank you", "Hello", "Goodbye"], "answer": "Thank you", "explanation": "謝謝 = Thank you!", "tags": ["phrases"]},

    # === Grade 2 Science (小二科學) ===
    {"subject": "science", "grade": 2, "difficulty": 2, "type": "choice", "content": "水在幾度會結冰？", "options": ["0°C", "10°C", "50°C", "100°C"], "answer": "0°C", "explanation": "水在0°C（冰點）會結冰", "tags": ["物理"]},
    {"subject": "science", "grade": 2, "difficulty": 1, "type": "choice", "content": "彩虹有幾種顏色？", "options": ["5種", "6種", "7種", "8種"], "answer": "7種", "explanation": "紅橙黃綠藍靛紫，共7種顏色🌈", "tags": ["自然現象"]},
    {"subject": "science", "grade": 2, "difficulty": 3, "type": "choice", "content": "蜻蜓有幾隻腳？", "options": ["4隻", "6隻", "8隻", "10隻"], "answer": "6隻", "explanation": "蜻蜓是昆蟲，有6隻腳", "tags": ["昆蟲"]},
    {"subject": "science", "grade": 2, "difficulty": 2, "type": "choice", "content": "磁鐵的哪個部分吸力最強？", "options": ["中間", "兩極", "側面", "都一樣"], "answer": "兩極", "explanation": "磁鐵的兩端（南極和北極）吸力最強", "tags": ["磁力"]},

    # === Grade 3 Math (小三數學) ===
    {"subject": "math", "grade": 3, "difficulty": 2, "type": "choice", "content": "125 + 238 = ?", "options": ["353", "363", "368", "373"], "answer": "363", "explanation": "125+238=363", "tags": ["加法", "三位數"]},
    {"subject": "math", "grade": 3, "difficulty": 3, "type": "choice", "content": "9 × 9 = ?", "options": ["72", "81", "90", "99"], "answer": "81", "explanation": "九九八十一", "tags": ["乘法"]},
    {"subject": "math", "grade": 3, "difficulty": 3, "type": "choice", "content": "一根繩子長2米，剪去80厘米，還剩多少？", "options": ["120厘米", "1米2厘米", "80厘米", "100厘米"], "answer": "120厘米", "explanation": "2米=200厘米，200-80=120厘米", "tags": ["應用題", "長度"]},
    {"subject": "math", "grade": 3, "difficulty": 4, "type": "input", "content": "144 ÷ 12 = ?", "answer": "12", "explanation": "144除以12等於12", "tags": ["除法"]},
    {"subject": "math", "grade": 3, "difficulty": 2, "type": "choice", "content": "下列哪個分數最大？", "options": ["1/2", "1/3", "1/4", "1/5"], "answer": "1/2", "explanation": "分子相同時，分母越小值越大", "tags": ["分數"]},
    {"subject": "math", "grade": 3, "difficulty": 4, "type": "choice", "content": "一個班有36人，平均分成4組，每組幾人？", "options": ["8人", "9人", "10人", "12人"], "answer": "9人", "explanation": "36÷4=9", "tags": ["除法", "應用題"]},
    {"subject": "math", "grade": 3, "difficulty": 5, "type": "choice", "content": "小明每分鐘走60米，15分鐘走多少米？", "options": ["800米", "900米", "950米", "1000米"], "answer": "900米", "explanation": "60×15=900", "tags": ["應用題", "速度"]},

    # === Grade 3 Chinese (小三語文) ===
    {"subject": "chinese", "grade": 3, "difficulty": 2, "type": "choice", "content": "「依依不捨」是什麼意思？", "options": ["非常高興", "不願離開", "生氣難過", "害怕恐懼"], "answer": "不願離開", "explanation": "依依不捨形容捨不得分離", "tags": ["成語"]},
    {"subject": "chinese", "grade": 3, "difficulty": 3, "type": "choice", "content": "下列哪個是擬人句？", "options": ["花兒開了", "花兒對我微笑", "花兒很美", "花兒是紅色的"], "answer": "花兒對我微笑", "explanation": "把花當成人來描寫（微笑）就是擬人", "tags": ["修辭"]},
    {"subject": "chinese", "grade": 3, "difficulty": 2, "type": "choice", "content": "「三心二意」中的數字共代表？", "options": ["3", "5", "2", "6"], "answer": "5", "explanation": "三+二=5，形容心思不專一", "tags": ["成語", "數字"]},
    {"subject": "chinese", "grade": 3, "difficulty": 4, "type": "choice", "content": "「如果...就...」是什麼關係的關聯詞？", "options": ["因果", "條件", "轉折", "並列"], "answer": "條件", "explanation": "如果...就...表示條件關係", "tags": ["語法"]},

    # === Grade 3 English (小三英語) ===
    {"subject": "english", "grade": 3, "difficulty": 2, "type": "choice", "content": "What's the past tense of \"go\"?", "options": ["goed", "went", "gone", "going"], "answer": "went", "explanation": "go → went (過去式)", "tags": ["tense", "irregular"]},
    {"subject": "english", "grade": 3, "difficulty": 3, "type": "choice", "content": "Choose: \"She ___ to school every day.\"", "options": ["go", "goes", "going", "gone"], "answer": "goes", "explanation": "第三人稱單數加 -es", "tags": ["grammar"]},
    {"subject": "english", "grade": 3, "difficulty": 2, "type": "choice", "content": "What season comes after winter?", "options": ["Summer", "Autumn", "Spring", "Fall"], "answer": "Spring", "explanation": "Winter → Spring (春天)", "tags": ["seasons"]},
    {"subject": "english", "grade": 3, "difficulty": 4, "type": "choice", "content": "Which is correct? \"There ___ many books.\"", "options": ["is", "are", "was", "be"], "answer": "are", "explanation": "books是複數，用are", "tags": ["grammar", "plural"]},

    # === Grade 3 Science (小三科學) ===
    {"subject": "science", "grade": 3, "difficulty": 3, "type": "choice", "content": "地球繞太陽轉一圈需要多久？", "options": ["一天", "一個月", "一年", "十年"], "answer": "一年", "explanation": "地球公轉太陽一周約365天（一年）", "tags": ["天文"]},
    {"subject": "science", "grade": 3, "difficulty": 2, "type": "choice", "content": "下列哪個不是哺乳動物？", "options": ["狗", "貓", "企鵝", "鯨魚"], "answer": "企鵝", "explanation": "企鵝是鳥類，不是哺乳動物", "tags": ["動物分類"]},
    {"subject": "science", "grade": 3, "difficulty": 4, "type": "choice", "content": "光的速度大約是每秒多少？", "options": ["3萬公里", "30萬公里", "300萬公里", "300公里"], "answer": "30萬公里", "explanation": "光速約30萬公里/秒", "tags": ["物理"]},
    {"subject": "science", "grade": 3, "difficulty": 3, "type": "choice", "content": "植物通過什麼過程製造養分？", "options": ["呼吸作用", "光合作用", "蒸散作用", "消化作用"], "answer": "光合作用", "explanation": "植物通過光合作用將陽光轉化為養分", "tags": ["植物", "生物"]},
    {"subject": "science", "grade": 3, "difficulty": 5, "type": "choice", "content": "水的三態不包括下列哪個？", "options": ["固態（冰）", "液態（水）", "氣態（水蒸氣）", "等離子態"], "answer": "等離子態", "explanation": "水的三態是固態、液態、氣態", "tags": ["物理", "物質"]},

    # === Grade 1 Fill-blank (小一填空題) ===
    {"subject": "math", "grade": 1, "difficulty": 1, "type": "fill_blank", "content": "比5大又比8小的數是 ___ 和 ___", "answer": "6|7", "explanation": "5 < 6 < 7 < 8，所以是6和7", "tags": ["比較大小", "數字"], "avg_time_sec": 20},
    {"subject": "chinese", "grade": 1, "difficulty": 1, "type": "fill_blank", "content": "「大」的反義詞是 ___", "answer": "小", "explanation": "大和小是反義詞", "tags": ["反義詞"], "avg_time_sec": 10},
    {"subject": "english", "grade": 1, "difficulty": 2, "type": "fill_blank", "content": "I see a red ___. (蘋果)", "answer": "apple", "explanation": "蘋果的英文是 apple", "tags": ["vocabulary", "fruits"], "avg_time_sec": 15},

    # === Grade 2 Fill-blank (小二填空題) ===
    {"subject": "math", "grade": 2, "difficulty": 2, "type": "fill_blank", "content": "3 × ___ = 24，所以 ___ = 8", "answer": "8|8", "explanation": "24 ÷ 3 = 8", "tags": ["乘法", "除法"], "avg_time_sec": 20},
    {"subject": "chinese", "grade": 2, "difficulty": 2, "type": "fill_blank", "content": "春天的相反季節是 ___ 天", "answer": "秋", "explanation": "春和秋是相反季節", "tags": ["季節", "反義詞"], "avg_time_sec": 12},
    {"subject": "english", "grade": 2, "difficulty": 2, "type": "fill_blank", "content": "The opposite of \"hot\" is ___.", "answer": "cold", "explanation": "hot（熱）的反義詞是 cold（冷）", "tags": ["opposites", "vocabulary"], "avg_time_sec": 15},

    # === Grade 3 Fill-blank (小三填空題) ===
    {"subject": "math", "grade": 3, "difficulty": 3, "type": "fill_blank", "content": "長方形的面積 = ___ × ___", "answer": "長|寬", "explanation": "長方形面積 = 長 × 寬", "tags": ["幾何", "面積"], "avg_time_sec": 15},
    {"subject": "chinese", "grade": 3, "difficulty": 3, "type": "fill_blank", "content": "「 ___ 尺竿頭，更進 ___ 步」", "answer": "百|一", "explanation": "百尺竿頭，更進一步，意思是在已經很好的基礎上繼續努力", "tags": ["成語"], "avg_time_sec": 15},
    {"subject": "english", "grade": 3, "difficulty": 3, "type": "fill_blank", "content": "She ___ (go 的過去式) to the park yesterday.", "answer": "went", "explanation": "go 的過去式是 went", "tags": ["tense", "irregular"], "avg_time_sec": 12},
    {"subject": "science", "grade": 3, "difficulty": 2, "type": "fill_blank", "content": "植物通過 ___ 作用製造養分，需要陽光和 ___", "answer": "光合|水", "explanation": "光合作用需要陽光、水和二氧化碳", "tags": ["植物", "生物"], "avg_time_sec": 20},
]


def get_seed_questions():
    """Return list of Question objects from seed data."""
    return [Question(**q) for q in QUESTIONS]
