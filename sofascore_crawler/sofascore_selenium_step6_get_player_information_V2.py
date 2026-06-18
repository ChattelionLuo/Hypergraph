import json
import os
import time
import random
from selenium import webdriver
from seleniumwire import webdriver as seleniumwire_webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
import argparse
import time


def chrome_service():
    chromedriver_path = os.environ.get("CHROMEDRIVER_PATH")
    if chromedriver_path:
        return Service(executable_path=chromedriver_path)
    return Service(ChromeDriverManager().install())


def apply_chrome_binary(options):
    chrome_binary = os.environ.get("CHROME_BINARY")
    if chrome_binary:
        options.binary_location = chrome_binary


def proxy_options_from_env(proxy_name):
    env_key = f"SOFASCORE_{proxy_name.upper()}_URL"
    proxy_url = os.environ.get(env_key) or os.environ.get("SOFASCORE_PROXY_URL")
    if not proxy_url:
        raise RuntimeError(
            f"Proxy driver {proxy_name!r} requires {env_key} or SOFASCORE_PROXY_URL"
        )
    return {
        'proxy': {
            'http': proxy_url,
            'https': proxy_url,
            'no_proxy': 'localhost,127.0.0.1'
        },
        'suppress_connection_errors': True,
    }

# 专门为数据爬取优化的版本
def create_proxy1_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    # chrome_options.add_argument('--no-sandbox')
    
    # ✅ 保留数据获取必需的功能
    # chrome_options.add_argument('--disable-javascript')  # 不禁用！
    chrome_options.add_argument('--disable-images')       # 可以禁用
    chrome_options.add_argument('--disable-plugins')      # 可以禁用
    
    apply_chrome_binary(chrome_options)
    
    seleniumwire_options = proxy_options_from_env("proxy1")
    
    service = chrome_service()

    driver = seleniumwire_webdriver.Chrome(service=service, options=chrome_options, seleniumwire_options=seleniumwire_options)

    # 🎯 只阻止明确的广告和追踪，保留可能的数据
    def data_preserving_interceptor(request):
        block_keywords = [
            'google-analytics', 'googletagmanager', 'googlesyndication',
            'doubleclick', 'facebook.com', 'twitter.com',
            'adnxs.com', 'amazon-adsystem', 'adtrafficquality'
        ]
        
        if any(keyword in request.url.lower() for keyword in block_keywords):
            request.abort()
    
    driver.request_interceptor = data_preserving_interceptor
    return driver

def create_proxy2_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    # chrome_options.add_argument('--no-sandbox')
    
    # ✅ 保留数据获取必需的功能
    # chrome_options.add_argument('--disable-javascript')  # 不禁用！
    chrome_options.add_argument('--disable-images')       # 可以禁用
    chrome_options.add_argument('--disable-plugins')      # 可以禁用
    
    apply_chrome_binary(chrome_options)
    
    seleniumwire_options = proxy_options_from_env("proxy2")
    
    service = chrome_service()

    driver = seleniumwire_webdriver.Chrome(service=service, options=chrome_options, seleniumwire_options=seleniumwire_options)

    # 🎯 只阻止明确的广告和追踪，保留可能的数据
    def data_preserving_interceptor(request):
        block_keywords = [
            'google-analytics', 'googletagmanager', 'googlesyndication',
            'doubleclick', 'facebook.com', 'twitter.com',
            'adnxs.com', 'amazon-adsystem', 'adtrafficquality'
        ]
        
        if any(keyword in request.url.lower() for keyword in block_keywords):
            request.abort()
    
    driver.request_interceptor = data_preserving_interceptor
    return driver

def create_proxy3_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    # chrome_options.add_argument('--no-sandbox')
    
    # ✅ 保留数据获取必需的功能
    # chrome_options.add_argument('--disable-javascript')  # 不禁用！
    chrome_options.add_argument('--disable-images')       # 可以禁用
    chrome_options.add_argument('--disable-plugins')      # 可以禁用
    
    apply_chrome_binary(chrome_options)
    
    seleniumwire_options = proxy_options_from_env("proxy3")
    
    service = chrome_service()

    driver = seleniumwire_webdriver.Chrome(service=service, options=chrome_options, seleniumwire_options=seleniumwire_options)

    # 🎯 只阻止明确的广告和追踪，保留可能的数据
    def data_preserving_interceptor(request):
        block_keywords = [
            'google-analytics', 'googletagmanager', 'googlesyndication',
            'doubleclick', 'facebook.com', 'twitter.com',
            'adnxs.com', 'amazon-adsystem', 'adtrafficquality'
        ]
        
        if any(keyword in request.url.lower() for keyword in block_keywords):
            request.abort()
    
    driver.request_interceptor = data_preserving_interceptor
    return driver

def create_proxy4_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    # chrome_options.add_argument('--no-sandbox')
    
    # ✅ 保留数据获取必需的功能
    # chrome_options.add_argument('--disable-javascript')  # 不禁用！
    chrome_options.add_argument('--disable-images')       # 可以禁用
    chrome_options.add_argument('--disable-plugins')      # 可以禁用
    
    apply_chrome_binary(chrome_options)
    
    seleniumwire_options = proxy_options_from_env("proxy4")
    
    service = chrome_service()

    driver = seleniumwire_webdriver.Chrome(service=service, options=chrome_options, seleniumwire_options=seleniumwire_options)

    # 🎯 只阻止明确的广告和追踪，保留可能的数据
    def data_preserving_interceptor(request):
        block_keywords = [
            'google-analytics', 'googletagmanager', 'googlesyndication',
            'doubleclick', 'facebook.com', 'twitter.com',
            'adnxs.com', 'amazon-adsystem', 'adtrafficquality'
        ]
        
        if any(keyword in request.url.lower() for keyword in block_keywords):
            request.abort()
    
    driver.request_interceptor = data_preserving_interceptor
    return driver

def create_proxy5_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    # chrome_options.add_argument('--no-sandbox')
    
    # ✅ 保留数据获取必需的功能
    # chrome_options.add_argument('--disable-javascript')  # 不禁用！
    chrome_options.add_argument('--disable-images')       # 可以禁用
    chrome_options.add_argument('--disable-plugins')      # 可以禁用
    
    apply_chrome_binary(chrome_options)
    
    seleniumwire_options = proxy_options_from_env("proxy5")
    
    service = chrome_service()

    driver = seleniumwire_webdriver.Chrome(service=service, options=chrome_options, seleniumwire_options=seleniumwire_options)

    # 🎯 只阻止明确的广告和追踪，保留可能的数据
    def data_preserving_interceptor(request):
        block_keywords = [
            'google-analytics', 'googletagmanager', 'googlesyndication',
            'doubleclick', 'facebook.com', 'twitter.com',
            'adnxs.com', 'amazon-adsystem', 'adtrafficquality'
        ]
        
        if any(keyword in request.url.lower() for keyword in block_keywords):
            request.abort()
    
    driver.request_interceptor = data_preserving_interceptor
    return driver

def create_proxy6_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    # chrome_options.add_argument('--no-sandbox')
    
    # ✅ 保留数据获取必需的功能
    # chrome_options.add_argument('--disable-javascript')  # 不禁用！
    chrome_options.add_argument('--disable-images')       # 可以禁用
    chrome_options.add_argument('--disable-plugins')      # 可以禁用
    
    apply_chrome_binary(chrome_options)
    
    seleniumwire_options = proxy_options_from_env("proxy6")
    
    service = chrome_service()

    driver = seleniumwire_webdriver.Chrome(service=service, options=chrome_options, seleniumwire_options=seleniumwire_options)

    # 🎯 只阻止明确的广告和追踪，保留可能的数据
    def data_preserving_interceptor(request):
        block_keywords = [
            'google-analytics', 'googletagmanager', 'googlesyndication',
            'doubleclick', 'facebook.com', 'twitter.com',
            'adnxs.com', 'amazon-adsystem', 'adtrafficquality'
        ]
        
        if any(keyword in request.url.lower() for keyword in block_keywords):
            request.abort()
    
    driver.request_interceptor = data_preserving_interceptor
    return driver


def create_local_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--disable-images')       # 可以禁用
    chrome_options.add_argument('--disable-plugins')      # 可以禁用
    
    apply_chrome_binary(chrome_options)
    
    service = chrome_service()
    
    driver = webdriver.Chrome(service=service, options=chrome_options)

        # 🎯 只阻止明确的广告和追踪，保留可能的数据
    def data_preserving_interceptor(request):
        block_keywords = [
            'google-analytics', 'googletagmanager', 'googlesyndication',
            'doubleclick', 'facebook.com', 'twitter.com',
            'adnxs.com', 'amazon-adsystem', 'adtrafficquality'
        ]
        
        if any(keyword in request.url.lower() for keyword in block_keywords):
            request.abort()
    
    driver.request_interceptor = data_preserving_interceptor
    
    return driver


def process_links(input_links, output_filename, error_filename, attempt_number=1, max_attempts=2, driver_type='local'):
    """
    处理链接列表的函数
    
    Args:
        input_links: 要处理的链接列表
        output_filename: 成功结果输出文件
        error_filename: 错误结果输出文件
        driver: Selenium WebDriver实例
        attempt_number: 当前尝试次数
        max_attempts: 最大尝试次数
    
    Returns:
        error_links: 失败的链接列表
    """
    fout = open(output_filename, "a", encoding="utf-8")
    ferror = open(error_filename, "a", encoding="utf-8")
    error_links = []
    
    print(f"\n========== 第 {attempt_number} 轮处理开始 ==========")
    print(f"待处理链接数量: {len(input_links)}")
    
    for idx, linkinfo in enumerate(input_links):
        # ===========爬取每个赛事 ================
        url = linkinfo["player_link"]
        print(f"正在处理链接：{url}")
        short_name = linkinfo["player_name"]
        print(f"({idx+1}/{len(input_links)}) 处理 {short_name} ...")
        success = False
        error_message = 'None'       
        time.sleep(random.uniform(10, 25))  # 每个URL间暂停
        for attempt in range(1):
            try:
                # print(driver_type)
                if driver_type == 'proxy1':
                    driver = create_proxy1_driver()
                elif driver_type == 'proxy2':
                    driver = create_proxy2_driver()
                elif driver_type == 'proxy3':
                    driver = create_proxy3_driver()
                elif driver_type == 'proxy4':
                    driver = create_proxy4_driver()
                elif driver_type == 'proxy5':
                    driver = create_proxy5_driver()
                elif driver_type == 'proxy6':
                    driver = create_proxy6_driver()
                else:
                    driver = create_local_driver()

                driver.set_page_load_timeout(30)  # 设置最大等待30秒
                driver.command_executor._timeout = 30  # 这是关键设置
                print(f"ChromeDriver port: {driver.service.port}")
                driver.get(url)
                print(f"访问成功")

                player_div=WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-panelid='details'].TabPanel.bpHovE"))
                    )            
                #####personal information
                personal_information_div = player_div.find_element(
                                                        By.XPATH,
                                                        ".//div[contains(@class, 'd_flex')"
                                                        " and contains(@class, 'flex-d_column')"
                                                        " and contains(@class, 'md:flex-d_row')"
                                                        " and contains(@class, 'md:p_sm')"
                                                        " and contains(@class, 'gap_sm')]"
                                                    )
                
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight * {});".format(random.uniform(0.2, 1.0)))
                time.sleep(random.uniform(0.2, 0.7))  # 滑动后小暂停

                per_div = personal_information_div.find_elements(
                    By.XPATH,
                    ".//div[contains(@class, 'd_flex')"
                    " and contains(@class, 'flex-d_column')"
                    " and contains(@class, 'w_100%')"
                    " and contains(@class, 'md:w_1/2')"
                    " and contains(@class, 'gap_sm')]"
                )


                record={}
                personal_information_keys = []
                personal_information_values = []

                driver.execute_script("window.scrollTo(0, document.body.scrollHeight * {});".format(random.uniform(2.0, 3.0)))
                time.sleep(random.uniform(0.5, 1.5))  # 滑动后小暂停

                for row in per_div:
                    main_class = row.find_elements(
                            By.XPATH,
                            ".//div[contains(@class, 'd_block') and (contains(@class, 'md:d_block') or contains(@class, 'md:d_none'))]"
                        )
                    for per_main_class in main_class:
                        main_class_name=per_main_class.find_element(By.CSS_SELECTOR, "span")
                        # print(f"main statistic feature: {main_class_name.text}")
                        if main_class_name.text == "Profile":
                            information = row.find_element(
                                                By.XPATH,
                                                ".//div[contains(@class, 'd_flex')"
                                                " and contains(@class, 'ai_center')"
                                                " and contains(@class, 'jc_center')"
                                                " and contains(@class, 'py_sm')"
                                                " and contains(@class, 'flex-wrap_wrap')"
                                                " and contains(@class, 'flex-d_column')"
                                                " and contains(@class, 'md:flex-d_row')]"
                                            )
                            # information_spans = information.find_elements(
                            #                                     By.XPATH,
                            #                                     ".//span[string-length(normalize-space(text())) > 0]"
                            #                                 )
                            information_spans = information.find_elements(
                                                                By.XPATH,
                                                                ".//span[not(.//span)]"
                                                            )
                            try:
                                for i, span in enumerate(information_spans):
                                    if i % 2 == 0:  # 偶数索引为键
                                        personal_information_keys.append(main_class_name.text + "_" + span.text)
                                        personal_information_values.append(information_spans[i+1].text)
                            except Exception as e:
                                pass
                        # elif main_class_name.text == "Rankings":
                        #     information = row.find_elements(
                        #                                 By.XPATH,
                        #                                 ".//div[contains(@class, 'pb_md')]"
                        #                             )[0]
                        #     information_spans = information.find_elements(
                        #                                         By.XPATH,
                        #                                         ".//span[not(.//span)]"
                        #                                     )[:4]
                        #     try:
                        #         for i, span in enumerate(information_spans):
                        #             if i % 2 == 0:  # 偶数索引为键
                        #                 personal_information_keys.append(main_class_name.text + "_" + span.text)
                        #                 personal_information_values.append(information_spans[i+1].text)
                        #     except Exception as e:
                        #         pass

                        # else:
                        #     information = row.find_elements(
                        #                                 By.XPATH,
                        #                                 ".//div[contains(@class, 'pb_sm') and contains(@class, 'md:pb_lg')]"
                        #                             )[0]
                        #     information_spans = information.find_elements(
                        #                                         By.XPATH,
                        #                                         ".//span[not(.//span)]"
                        #                                     )
                        #     try:
                        #         for i, span in enumerate(information_spans):
                        #             if i % 2 == 0:  # 偶数索引为键
                        #                 personal_information_keys.append(main_class_name.text + "_" + span.text)
                        #                 personal_information_values.append(information_spans[i+1].text)
                        #     except Exception as e:
                        #         pass
                
                # print(f"统计信息：{len(statistics_keys)} 个特征")
                # print(f"统计信息：{len(statistics_values)} 个值")
                record = {
                    "short_name": short_name,
                    "player_link": url,
                    
                    }      
                record.update({key: value for key, value in zip(personal_information_keys, personal_information_values)})
                
                fout.write(json.dumps(record, ensure_ascii=False) + "\n")
                fout.flush()
                print(f"   √ 完成：{short_name}")
                success = True
                break
            except Exception as e:
                print(f"   × 第 {attempt+1} 次失败：{short_name} 错误信息：{e}")
                error_message = error_message+f"Error: {str(e)}"
            finally:
                driver.quit()

            if not success:
                print(f"彻底失败，跳过：{short_name}")
                error_record = {
                    "short_name": short_name,
                    "player_link": url,
                    "condition": "error",
                }
                # 同时写入输出文件和错误文件
                fout.write(json.dumps(error_record, ensure_ascii=False) + "\n")
                ferror.write(json.dumps(linkinfo, ensure_ascii=False) + "\n")
                fout.flush()
                ferror.flush()
                error_links.append(linkinfo)

                time.sleep(random.uniform(40, 60))  # 每个URL间暂停
                continue

            


    fout.close()
    ferror.close()
    return error_links

def load_links_from_file(filename):
    """从文件加载链接"""
    links = []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:  # 跳过空行
                    item = json.loads(line)
                    links.append(item)
    except FileNotFoundError:
        print(f"文件 {filename} 不存在")
    return links

def clear_file(filename):
    """清空文件内容"""
    with open(filename, "w", encoding="utf-8") as f:
        pass

# =========== 主程序 ================
def main(input_filename, output_filename, error_filename, driver_type='local'):
    # 文件配置
    max_attempts = 3  # 最大重试次数

    # # 设置 Selenium Chrome
    # chrome_options = Options()
    # chrome_options.add_argument("--headless")
    # chrome_options.add_argument("--no-sandbox")
    # chrome_options.add_argument("--disable-dev-shm-usage")
    # chrome_options.binary_location = "/home/24121534r/chrome/chrome"
    
    # service = Service(executable_path="/home/24121534r/chrome/chromedriver")
    # driver = webdriver.Chrome(service=service, options=chrome_options)
    # print(f"ChromeDriver port: {driver.service.port}")
    
    try:
        # 第一次处理：从原始输入文件开始
        print("开始处理原始链接文件...")
        input_links = load_links_from_file(input_filename)
        
        if not input_links:
            print(f"输入文件 {input_filename} 为空或不存在")
            return
        
        # 清空错误文件
        clear_file(error_filename)
        
        # 处理链接
        error_links = process_links(input_links, output_filename, error_filename, 1, max_attempts, driver_type=driver_type)
        
        # 重试处理错误链接
        attempt_number = 2
        while error_links and attempt_number <= max_attempts:
            print(f"\n========== 开始第 {attempt_number} 轮重试 ==========")
            print(f"错误链接数量: {len(error_links)}")
            
            # 清空错误文件，准备下一轮
            clear_file(error_filename)
            
            # 处理错误链接
            error_links = process_links(error_links, output_filename, error_filename, attempt_number, max_attempts, driver_type=driver_type)
            attempt_number += 1
        
        # 最终结果
        if not error_links:
            print(f"\n========== 全部处理完成！ ==========")
            print(f"所有链接都已成功处理")
        else:
            print(f"\n========== 处理结束 ==========")
            print(f"达到最大重试次数 ({max_attempts})，仍有 {len(error_links)} 个链接失败")
            print(f"失败的链接已保存在 {error_filename}")
        
        print(f"成功结果保存在 {output_filename}")
        
    finally:
        print("浏览器已关闭")

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

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Process tennis match data from SofaScore')
    parser.add_argument('--input', help='Input JSONL with player links')
    parser.add_argument('--output', help='Output JSONL with player information')
    parser.add_argument('--error', help='Error JSONL for failed player links')
    parser.add_argument('--input_ATP', default='US_Open', 
                        help='Input file with match links')
    parser.add_argument('--year', type=int, default=2020, 
                        help='Year of the matches to process')
    parser.add_argument('--driver_type', type=str,default='proxy6', choices=['local', 'proxy1', 'proxy2', 'proxy3', 'proxy4', 'proxy5', 'proxy6'],
                            help='Type of the Selenium driver to use')

    args = parser.parse_args()

    # input_filename = f"filtered_grand_slam_2016_2025_ft_splits/players_link_part3.jsonl"
    # # input_filename = f"filtered_grand_slam_2016_2025_ft_splits/{args.input_ATP}_{args.year}_step4_error.jsonl"
    # output_filename = f"filtered_grand_slam_2016_2025_ft_splits/players_part3_information.jsonl"
    # error_filename = f"filtered_grand_slam_2016_2025_ft_splits/players_part3_information_error.jsonl"

    input_filename = args.input or "data/player/players_link_rest_part7.jsonl"
    output_filename = args.output or "data/player/players_rest_part7_information.jsonl"
    error_filename = args.error or "data/player/players_rest_part7_information_error.jsonl"


    start_time = time.time()
    main(input_filename, output_filename, error_filename, driver_type=args.driver_type)
    end_time = time.time()
    print(f"处理完成，耗时 {end_time - start_time:.2f} 秒")
