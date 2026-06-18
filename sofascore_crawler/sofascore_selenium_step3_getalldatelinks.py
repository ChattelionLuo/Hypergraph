import json
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# =========== 1. 读取所有年份和赛事链接 ================
# input_filename = "all_ATP_competition_year_links.jsonl"
# output_filename = "all_ATP_competition_year_date_links.jsonl"
input_filename = "error_year_links_V2.jsonl"
output_filename = "error_year_date_links_V2.jsonl"
input_links = []
with open(input_filename, "r", encoding="utf-8") as f:
    for line in f:
        item = json.loads(line.strip())
        # 拼接 ,tab:matches
        item['href'] = item['href'].split(',tab:')[0] + ",tab:matches"
        input_links.append(item)

# # =========== 2. 设置 Selenium Chrome ================
# chrome_options = Options()
# chrome_options.add_argument("--headless")
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--disable-dev-shm-usage")

# chrome_options.binary_location = "/home/24121534r/chrome/chrome"

# # 指定 chromedriver 路径
# service = Service(executable_path="/home/24121534r/chrome/chromedriver")

# driver = webdriver.Chrome(service=service, options=chrome_options)
# print(f"ChromeDriver port: {driver.service.port}")

class SmoothScroller:
    def __init__(self, driver):
        self.driver = driver
    
    def scroll_to_bottom(self, method='smooth', **kwargs):
        """
        滚动到页面底部的主方法
        
        Args:
            method: 滚动方法 ('smooth', 'natural', 'infinite')
            **kwargs: 各种方法的特定参数
        """
        if method == 'smooth':
            return self._smooth_scroll(**kwargs)
        elif method == 'natural':
            return self._natural_scroll(**kwargs)
        elif method == 'infinite':
            return self._infinite_scroll(**kwargs)
        else:
            raise ValueError("方法必须是 'smooth', 'natural', 或 'infinite'")
    
    def _smooth_scroll(self, scroll_step=100, delay=0.1):
        """平滑滚动实现"""
        total_height = self.driver.execute_script("return document.body.scrollHeight")
        current_position = 0
        
        while current_position < total_height:
            self.driver.execute_script(f"window.scrollTo(0, {current_position});")
            current_position += scroll_step
            time.sleep(delay)
            
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height > total_height:
                total_height = new_height
        
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        return True
    
    def _natural_scroll(self, min_delay=0.1, max_delay=0.5):
        """自然滚动实现"""
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        while True:
            scroll_step = random.randint(100, 300)
            self.driver.execute_script(f"window.scrollBy(0, {scroll_step});")
            
            delay = random.uniform(min_delay, max_delay)
            time.sleep(delay)
            
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            current_bottom = self.driver.execute_script("return window.pageYOffset + window.innerHeight")
            
            if new_height == last_height and current_bottom >= new_height:
                break
            
            last_height = new_height
        
        return True
    
    def _infinite_scroll(self, max_scrolls=50, scroll_pause=2):
        """无限滚动实现"""
        scrolls = 0
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        while scrolls < max_scrolls:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause)
            
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            if new_height == last_height:
                break
            
            last_height = new_height
            scrolls += 1
        
        return scrolls

# =========== 3. 循环爬取每个年份赛事 ================
fout = open(output_filename, "a", encoding="utf-8")
results = []
for idx, linkinfo in enumerate(input_links):
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

    # ===========爬取每个赛事 ================
    url = linkinfo["href"]
    print(f"正在处理链接：{url}")
    ATP_competition = linkinfo["ATP_competition"]
    year = linkinfo["year"]
    if year == "error":
        print(f"跳过错误链接：{ATP_competition} {year}")
        success = False
    else:
        print(f"({idx+1}/{len(input_links)}) 处理 {ATP_competition} {year} ...")
        success = False
        for attempt in range(1):
            try:
                driver.get(url)
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-tabid='date']"))
                )
                try:
                    date_tab = driver.find_element(By.CSS_SELECTOR, "div[data-tabid='date']")
                    driver.execute_script("arguments[0].scrollIntoView(true);", date_tab)  # 滚动到标签位置
                    date_tab.click()
                    time.sleep(2)
                except Exception:
                    pass
                time.sleep(3)
                # 滚动以加载所有内容
                scroller = SmoothScroller(driver)
                scroller.scroll_to_bottom('smooth', scroll_step=50, delay=0.1)
                print("页面滚动加载成功。")
                time.sleep(1)
                match_panels = WebDriverWait(driver, 30).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[data-panelid='date'].TabPanel.bpHovE"))
                )
                time.sleep(2)
                for panel in match_panels:
                    match_links = panel.find_elements(By.CSS_SELECTOR, "a.sc-3f813a14-0")
                    for a_tag in match_links:
                        try:
                            match_href = a_tag.get_attribute("href")
                        except Exception:
                            match_href = ""
                        try:
                            date_elem = a_tag.find_element(By.CSS_SELECTOR, "div.Box.jKVshf > bdi.Text.kcRyBI")
                            date_str = date_elem.text.strip()
                        except Exception:
                            date_str = ""
                        try:
                            cond_elem = a_tag.find_element(By.CSS_SELECTOR, "div.Box.jKVshf span.Text.fjeMtb.currentScore > bdi")
                            condition = cond_elem.text.strip()
                        except Exception:
                            condition = ""
                        record = {
                            "ATP_competition": ATP_competition,
                            "year": year,
                            "date": date_str,
                            "conditions": condition,
                            "href": match_href
                        }
                        fout.write(json.dumps(record, ensure_ascii=False) + "\n")
                        fout.flush()
                print(f"   √ 完成：{ATP_competition} {year}")
                success = True
                break
            except Exception as e:
                print(f"   × 第 {attempt+1} 次失败：{ATP_competition} {year}，错误信息：{e}")
    if not success:
        print(f"   ××× 彻底失败，跳过：{ATP_competition} {year}")
        record = {
            "ATP_competition": ATP_competition,
            "year": year,
            "date": "error",
            "conditions": "error",
            "href": "error"
        }
        fout.write(json.dumps(record, ensure_ascii=False) + "\n")
        fout.flush()
        driver.quit()
        time.sleep(20)
        continue
    
    driver.quit()

fout.close()
driver.quit()
print(f"全部完成，结果保存在 {output_filename}")
