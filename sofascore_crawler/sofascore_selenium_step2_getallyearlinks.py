import json
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import random
from selenium.webdriver.common.action_chains import ActionChains
import json


input_file = "all_ATP_competition_links.jsonl"
output_file = "all_ATP_competition_year_links.jsonl"

# chrome_options = Options()
# chrome_options.add_argument("--headless")
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--disable-dev-shm-usage")

# chrome_options.binary_location = "/home/24121534r/chrome/chrome"

# # 指定 chromedriver 路径
# service = Service(executable_path="/home/24121534r/chrome/chromedriver")

# driver = webdriver.Chrome(service=service, options=chrome_options)
# print(f"ChromeDriver port: {driver.service.port}")

# def get_seasons(url):
#     for attempt in range(3):
#         try:
#             driver.get(url)
#             time.sleep(5)
#             html = driver.page_source
#             match = re.search(r'"seasons":(\[.*?\])', html)
#             if match:
#                 seasons_json = match.group(1)
#                 seasons = json.loads(seasons_json)
#                 return seasons
#             else:
#                 print(f"未找到seasons: {url}")
#                 return None
#         except Exception as e:
#             print(f"加载页面失败: {url}, 错误: {e}, 重试 {attempt+1}/3")
#             time.sleep(4)
    # return None

with open(input_file, "r", encoding="utf-8") as fin, \
     open(output_file, "w", encoding="utf-8") as fout:
    for line in fin:
            ###### 随机等待时间 ######
        wait_time = random.uniform(10, 20)
        time.sleep(wait_time)
        # =========== 2. 设置 Selenium Chrome ================
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        chrome_options.binary_location = "/home/24121534r/chrome/chrome"

        # 指定 chromedriver 路径
        service = Service(executable_path="/home/24121534r/chrome/chromedriver")

        driver = webdriver.Chrome(service=service, options=chrome_options)
        print(f"ChromeDriver port: {driver.service.port}")

        ##### 爬取每个赛事的年份链接 ######

        line = line.strip()
        if not line:
            continue
        item = json.loads(line)
        atp_name = item.get("ATP_competition", "")
        base_url = item.get("href", "")
        if 'Doubles' in atp_name:
            print(f"跳过双打赛事: {atp_name}")
        else :
            print(f"正在处理赛事: {atp_name} {base_url}")
            success = False
            seasons=None
            for attempt in range(3):
                try:
                    driver.get(base_url)
                    time.sleep(5)
                    html = driver.page_source
                    match = re.search(r'"seasons":(\[.*?\])', html)
                    if match:
                        seasons_json = match.group(1)
                        seasons = json.loads(seasons_json)

                    if not seasons:
                        # 失败时标记 year 为 error
                        out_line = {
                            "ATP_competition": atp_name,
                            "year": "error",
                            "href": base_url
                        }
                        fout.write(json.dumps(out_line, ensure_ascii=False) + "\n")
                        fout.flush()
                        print(f"{atp_name} 失败，已记录 error")
                    else:
                        for s in seasons:
                            year = s.get("year")
                            sid = s.get("id")
                            full_url = f"{base_url}#id:{sid}"
                            out_line = {
                                "ATP_competition": atp_name,
                                "year": year,
                                "href": full_url
                            }
                            fout.write(json.dumps(out_line, ensure_ascii=False) + "\n")
                            fout.flush()
                        print(f"{atp_name} 完成，共 {len(seasons)} 年份")
                    
                    success = True
                    break
                except Exception as e:
                    print(f"   × 第 {attempt+1} 次失败：{atp_name}，错误信息：{e}")
                    time.sleep(5)

            if not success:
                print(f"   ××× 彻底失败，跳过：{atp_name}")
                # 失败时标记 year 为 error
                out_line = {
                    "ATP_competition": atp_name,
                    "year": "error",
                    "href": base_url
                }
                fout.write(json.dumps(out_line, ensure_ascii=False) + "\n")
                fout.flush()
                continue

            driver.quit()

fout.close()
print("全部处理完成。")
