import re

def parse_text(text):
    sections = []
    lines = text.split('\n')
    current_section = {"title": "", "content": ""}
    
    for line in lines:
        match = re.match(r'^(#+)\s*(.*)', line)
        if match:
            if current_section["title"]:
                sections.append(current_section)
                current_section = {"title": "", "content": ""}
            
            current_section["title"] = match.group(2)
        else:
            current_section["content"] += line + "\n"
    
    if current_section["title"]:
        sections.append(current_section)
    
    return sections

# 測試用文章
test_text = """
### **1.**【目的**; Purpose**】:

為使同仁明確瞭解計假標準、各種假別及請假程序,當同仁有請假需求時,得以依 據辦理。

- **2.**【範圍**; Scope**】:
適用對象為本公司全體同仁。

### **3.**【參考資料**; Reference**】:

- 3.1 勞動基準法及施行細則
- 3.2 勞動部勞工請假規則
- 3.3 性別平等工作法及施行細則
- 3.4 出勤管理辦法
- 3.5 福委會福利措施

3.6 職務代理人公告作業程序

- 3.7 工時填寫管理辦法
- 3.8 員工獎懲作業程序

### **4.**【定義**; Terminology**】:

4.1 請假:同仁因故未能於原排班之上班時間正常出勤時,需依規定請假。

- 4.2 刷卡異常:指人資系統顯示出勤時數不足標準工時之異常資料。
- 4.3 刷卡制度:依「出勤管理辦法」規定時間刷卡上/下班。如上班地點無刷卡設備 或無法使用外勤打卡 APP (ex.軍政單位/偏鄉地區網路不穩…),則以 簽到/簽退表或客戶辦公地點之出勤系統刷卡資料匯回,作為出勤依

據,唯需記載至分鐘。

4.4 上/下班時間:依「出勤管理辦法」規定辦理,若同仁派駐於客戶辦公地點或外 點辦公室,上班時間則依客戶要求辦理(以出勤時數 8 小時為原 則)。

4.5 曠職:指依正常工作時間或已議訂之排班時間,應出勤而無故未出勤且未請假。 4.6 次日:人資系統設定是以﹝日曆天﹞為標準檢核。

"""

# 執行解析
parsed_sections = parse_text(test_text)

# 輸出結果
for section in parsed_sections:
    print(f"Title: {section['title']}")
    print(f"Content: {section['content'].strip()}\n")
