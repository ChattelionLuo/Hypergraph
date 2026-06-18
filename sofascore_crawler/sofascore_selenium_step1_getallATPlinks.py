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


# 设置 WebDriver
# 设置 Chrome 选项
chrome_options = Options()
chrome_options.add_argument("--headless")  # 如需无头模式可取消注释
# chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
# chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# 初始化服务和驱动
# service = Service(ChromeDriverManager().install()
# driver = webdriver.Chrome(service=service, options=chrome_options)
# driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
# driver = webdriver.Chrome(options=chrome_options)
# 指定本地 chrome 路径
chrome_options.binary_location = "/home/24121534r/chrome/chrome"

# 指定 chromedriver 路径
service = Service(executable_path="/home/24121534r/chrome/chromedriver")

driver = webdriver.Chrome(service=service, options=chrome_options)
print(f"ChromeDriver port: {driver.service.port}")
url="https://www.sofascore.com/tennis"

# 重试逻辑
max_retries = 3
for attempt in range(max_retries):
    try:
        print(f"第 {attempt + 1} 次尝试加载页面...")
        driver.get(url)
        # driver.execute_script("window.scrollBy(0, 80);")  # 向下滚动 100 像素，可根据需要调整
        screenshot_path = "screenshot.png"
        driver.save_screenshot(screenshot_path)
        print(f"截图已保存至 {screenshot_path}")
        competition_button= WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-tabid='competitions']")))
        print("找到competition_button")
        competition_button.click()
        time.sleep(3)
        a_elem = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href="/tennis/atp"]')))           
        print("找到ATP按钮。")
        a_elem.click()
        time.sleep(5)
        print("点击ATP按钮成功。")
        screenshot_path = "screenshot.png"
        driver.save_screenshot(screenshot_path)
        print(f"截图已保存至 {screenshot_path}")
        # # 滚动以加载所有内容
        # scroller = SmoothScroller(driver)
        # scroller.scroll_to_bottom('smooth', scroll_step=50, delay=0.1)
        # print("页面滚动加载成功。")
        break
    except Exception as e:
        print(f"错误: {e}")
        time.sleep(5)
else:
    print("所有尝试加载页面失败。")
    driver.quit()
    exit()

# 此时页面已刷新（不论是整体刷新，还是某区域重新渲染）
# 1. 重新用 driver 查找新的 a_elem
a_elem = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href="/tennis/atp"]'))
)
# 2. 从新的 a_elem 查找最新父级
parent_div = a_elem.find_element(
    By.XPATH,
    './ancestor::div[contains(@class, "Box") and contains(@class, "Flex") and contains(@class, "etwlSU") and contains(@class, "iWGVcA")]'
)
# print(parent_div.get_attribute('class'))

# target_div = parent_div.find_element(By.CSS_SELECTOR, 'div.d_flex.flex-d_column.bg_surface.s2')
target_div = parent_div.find_element(
    By.XPATH,
    './/div[contains(@class, "d_flex") and contains(@class, "flex-d_column") and contains(@class, "bg_surface") and contains(@class, "s2")]'
)
a_tags = target_div.find_elements(By.TAG_NAME, 'a')
# 假设 a_tags 已经是所有 <a> 元素的列表
data = []

for a in a_tags:
    href = a.get_attribute('href')
    try:
        # 直接在a里找span（建议用find_element，不要用driver全局找）
        name_span = a.find_element(By.CSS_SELECTOR, 'span')
        name = name_span.text.strip()
        data.append({"ATP_competition": name, "href": href})
    except Exception as e:
        print(f"找不到span，跳过一个a，错误信息: {e}")

# 写入 jsonl 文件
with open("all_ATP_competition_links.jsonl", "w", encoding="utf-8") as f:
    for item in data:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")




# hrefs = [a.get_attribute('href') for a in a_tags]
# print(hrefs)



