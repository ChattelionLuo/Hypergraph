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
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import argparse

class RealisticStealthConfig:
    """隐身配置"""
    
    STEALTH_LEVELS = {
        'minimal': {
            'delays': {'min': 2, 'max': 10, 'jitter': 0.3},
            'behavior_frequency': 0.1,
            'mouse_movements': False,
            'scroll_variety': False,
            'description': '快速测试模式'
        },
        'light': {
            'delays': {'min': 1, 'max': 3, 'jitter': 0.1},
            'behavior_frequency': 0.05,
            'mouse_movements': True,
            'scroll_variety': True,
            'description': '正常浏览速度'
        },
        'medium': {
            'delays': {'min': 25, 'max': 50, 'jitter': 0.5},
            'behavior_frequency': 0.5,
            'mouse_movements': True,
            'scroll_variety': True,
            'description': '仔细浏览模式'
        }
    }
    
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ]
    
    LANGUAGES = ["en-US,en;q=0.9", "en-GB,en;q=0.9"]

class RealisticStealthDriver:
    """隐身驱动器"""
    
    def __init__(self, proxy_config=None, stealth_level="light", chromedriver_path=None, chrome_binary_path=None):
        self.proxy_config = proxy_config
        self.config = RealisticStealthConfig.STEALTH_LEVELS[stealth_level]
        self.stealth_level = stealth_level
        self.user_agent = random.choice(RealisticStealthConfig.USER_AGENTS)
        self.language = random.choice(RealisticStealthConfig.LANGUAGES)
        self.chromedriver_path = chromedriver_path or os.environ.get("CHROMEDRIVER_PATH")
        self.chrome_binary_path = chrome_binary_path or os.environ.get("CHROME_BINARY")
        
    def create_driver(self):
        """创建隐身驱动"""
        options = self._create_realistic_options()
        if self.chromedriver_path:
            service = Service(executable_path=self.chromedriver_path)
        else:
            service = Service(ChromeDriverManager().install())
        
        if self.proxy_config:
            seleniumwire_options = self._setup_proxy()
            driver = seleniumwire_webdriver.Chrome(
                service=service, options=options, 
                seleniumwire_options=seleniumwire_options
            )
            driver.request_interceptor = self._create_smart_interceptor()
        else:
            driver = webdriver.Chrome(service=service, options=options)
        
        self._execute_stealth_scripts(driver)
        driver.set_page_load_timeout(45)
        driver.implicitly_wait(10)
        
        return driver
    
    def _create_realistic_options(self):
        """创建Chrome选项"""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument(f'--user-agent={self.user_agent}')
        options.add_argument(f'--lang={self.language.split(",")[0]}')
        options.add_argument('--disable-images')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-extensions')
        if self.chrome_binary_path:
            options.binary_location = self.chrome_binary_path
        return options
    
    def _setup_proxy(self):
        """设置代理"""
        proxy_url = self.proxy_config["url"]
        return {
            'proxy': {
                'http': proxy_url,
                'https': proxy_url,
                'no_proxy': 'localhost,127.0.0.1'
            },
            'suppress_connection_errors': True,
        }
    
    def _create_smart_interceptor(self):
        """智能请求拦截器"""
        def interceptor(request):
            block_domains = [
                'google-analytics.com', 'googletagmanager.com', 
                'googlesyndication.com', 'doubleclick.net',
                'facebook.com', 'adnxs.com'
            ]
            
            if any(domain in request.url.lower() for domain in block_domains):
                request.abort()
                return
            
            try:
                request.headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
                request.headers['Accept-Language'] = self.language
                request.headers['Accept-Encoding'] = 'gzip, deflate, br'
                request.headers['Connection'] = 'keep-alive'
            except Exception as e:
                print(f"⚠️  设置请求头失败: {e}")
    
        return interceptor
    
    def _execute_stealth_scripts(self, driver):
        """执行反检测脚本"""
        stealth_scripts = [
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});",
            "Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});",
            "window.chrome = {runtime: {}, app: {isInstalled: false}};"
        ]
        
        for script in stealth_scripts:
            try:
                driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': script})
            except:
                try:
                    driver.execute_script(script)
                except:
                    pass

class RealisticBehavior:
    """人类行为模拟器"""
    
    def __init__(self, driver, config):
        self.driver = driver
        self.config = config
        self.actions = ActionChains(driver)
    
    def smart_delay(self, context="normal"):
        """智能延迟"""
        base_min = self.config['delays']['min']
        base_max = self.config['delays']['max']
        
        if context == "page_load":
            base_min *= 0.8
            base_max *= 0.8
        elif context == "quick":
            base_min *= 0.3
            base_max *= 0.3
        
        base_delay = random.uniform(base_min, base_max)
        jitter = random.uniform(-self.config['delays']['jitter'], self.config['delays']['jitter']) * base_delay
        final_delay = max(1, base_delay + jitter)
        
        print(f"  ⏳ 等待 {final_delay:.1f} 秒...")
        time.sleep(final_delay)
    
    def conditional_behavior(self, behavior_func):
        """条件性执行行为"""
        if random.random() < self.config['behavior_frequency']:
            behavior_func()
    
    def realistic_scroll(self):
        """真实滚动"""
        if self.config['scroll_variety']:
            scroll_amount = random.randint(150, 400)
            self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            time.sleep(random.uniform(0.3, 0.8))

# 创建驱动函数
def create_driver(driver_type='local', stealth_level='light', chromedriver_path=None, chrome_binary_path=None):
    """创建驱动器"""
    proxy_config = None
    if driver_type != 'local':
        env_key = f"SOFASCORE_{driver_type.upper()}_URL"
        proxy_url = os.environ.get(env_key) or os.environ.get("SOFASCORE_PROXY_URL")
        if not proxy_url:
            raise RuntimeError(
                f"Proxy driver {driver_type!r} requires {env_key} or SOFASCORE_PROXY_URL"
            )
        proxy_config = {"url": proxy_url}
    stealth_driver = RealisticStealthDriver(proxy_config, stealth_level, chromedriver_path, chrome_binary_path)
    return stealth_driver.create_driver()

def extract_odds_only(input_links, output_filename, error_filename, 
                      attempt_number=1, max_attempts=2, driver_type='local', 
                      stealth_level='light', chromedriver_path=None, chrome_binary_path=None):
    """只提取odds的核心函数 - 只需要href"""
    
    fout = open(output_filename, "a", encoding="utf-8")
    ferror = open(error_filename, "a", encoding="utf-8")
    error_links = []
    
    config = RealisticStealthConfig.STEALTH_LEVELS[stealth_level]
    
    print(f"\n========== 第 {attempt_number} 轮处理开始 ==========")
    print(f"🔒 隐身级别: {stealth_level} - {config['description']}")
    print(f"📊 待处理链接: {len(input_links)} 个")
    print(f"🎯 目标: 只提取 odds（赔率）")
    
    for idx, linkinfo in enumerate(input_links):
        # 只需要href，其他字段可选
        url = linkinfo.get("href", "")
        
        if not url:
            print(f"⚠️  跳过空链接")
            continue
        
        print(f"\n📍 ({idx+1}/{len(input_links)}) 处理: {url}")
        success = False
        driver = None
        error_message = 'None'
        
        try:
            # 创建驱动
            driver = create_driver(driver_type, stealth_level, chromedriver_path, chrome_binary_path)
            behavior = RealisticBehavior(driver, config)
            
            print(f"🌐 ChromeDriver启动成功")
            
            # 主延迟
            behavior.smart_delay(context="normal")
            
            # 访问URL
            driver.get(url)
            print(f"✅ 页面访问成功")
            
            behavior.smart_delay(context="page_load")
            # screenshot_path = "screenshot_V3.png"
            # driver.save_screenshot(screenshot_path)
            
            # 等待主要内容
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.d_flex.flex-wrap_wrap.gap_md"))
                
            )


            # ============ 先点击按钮，查看HTML ============
            try:
                print("🔍 查找 Additional odds 按钮...")

                # 找到按钮（即使被遮挡也能找到）
                additional_btn = driver.find_element(By.XPATH, 
                    "//*[contains(text(), 'Additional odds')]"
                )
                print("✅ 找到按钮")
                
                # ✅ 用 JavaScript 点击（不受遮挡影响）
                driver.execute_script("arguments[0].click();", additional_btn)
                print("✅ 点击成功")
                
                time.sleep(2)
                screenshot_path = "screenshot_V3.png"
                driver.save_screenshot(screenshot_path)
                                
            except Exception as e:
                print(f"❌ 错误: {e}")

            # ✅ 直接在整个页面找，不限定在 main_div 下
            additional_container = driver.find_element(By.CSS_SELECTOR, "div.pos_relative.p_md")
            print("✅ 找到容器 div.pos_relative.p_md")

            # 提取完整文本
            full_text = additional_container.text
            print(f"\n📝 展开后的完整文本:\n{full_text}\n")
            
            # ========== 精确提取每个字段 ==========
            lines = [line.strip() for line in full_text.split('\n') if line.strip()]
            print(f"📊 共 {len(lines)} 行数据: {lines}")
            
            
            # ============ 构建记录（保留原有字段但使用默认值） ============
            record = {
                "href": url,
                "odds_information": lines,
            }
            
            # 如果原始数据有这些字段，也保存下来
            for key in ['ATP_competition', 'year', 'date', 'conditions']:
                if key in linkinfo:
                    record[key] = linkinfo[key]
            
            # 保存记录
            fout.write(json.dumps(record, ensure_ascii=False) + "\n")
            fout.flush()
            
            print(f"✅ 成功提取odds: {lines}")
            success = True
            
        except TimeoutException as e:
            print(f"⏰ 超时失败: {e}")
            error_message = f"Timeout: {str(e)}"
            
        except Exception as e:
            print(f"❌ 异常失败: {e}")
            error_message = f"Error: {str(e)}"
            
        finally:
            if driver:
                try:
                    driver.quit()
                    print("🔒 浏览器已关闭")
                except Exception as quit_error:
                    print(f"⚠️  浏览器关闭异常: {quit_error}")
        
        if not success:
            print(f"💔 处理失败: {url}")
            error_record = {
                "href": url,
                "attempt_number": attempt_number,
                "error_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "error_message": error_message
            }
            
            # 保留原始信息
            error_record.update(linkinfo)
            
            fout.write(json.dumps(error_record, ensure_ascii=False) + "\n")
            ferror.write(json.dumps(linkinfo, ensure_ascii=False) + "\n")
            fout.flush()
            ferror.flush()
            error_links.append(linkinfo)
            
            # 失败后延迟
            failure_delay = config['delays']['max'] * 3
            print(f"😴 失败后等待 {failure_delay:.1f} 秒...")
            time.sleep(failure_delay)
    
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
                if line:
                    item = json.loads(line)
                    links.append(item)
    except FileNotFoundError:
        print(f"❌ 文件 {filename} 不存在")
    return links

def clear_file(filename):
    """清空文件"""
    with open(filename, "w", encoding="utf-8") as f:
        pass

def main(input_filename, output_filename, error_filename, driver_type='local', 
         stealth_level='light', chromedriver_path=None, chrome_binary_path=None):
    """主函数"""
    max_attempts = 3
    
    config = RealisticStealthConfig.STEALTH_LEVELS[stealth_level]
    print(f"🚀 简化版赔率爬虫启动")
    print(f"🎯 目标: 只提取 odds（赔率）")
    print(f"🔒 隐身级别: {stealth_level.upper()} ({config['description']})")
    print(f"⏱️  延迟范围: {config['delays']['min']}-{config['delays']['max']}秒")
    print(f"🌐 驱动类型: {driver_type}")
    
    try:
        input_links = load_links_from_file(input_filename)
        
        if not input_links:
            print(f"❌ 输入文件 {input_filename} 为空或不存在")
            return
        
        print(f"📂 成功加载 {len(input_links)} 个链接")
        
        clear_file(error_filename)
        
        error_links = extract_odds_only(
            input_links, output_filename, error_filename, 
            1, max_attempts, driver_type=driver_type, stealth_level=stealth_level,
            chromedriver_path=chromedriver_path, chrome_binary_path=chrome_binary_path
        )
        
        # 重试逻辑
        attempt_number = 2
        while error_links and attempt_number <= max_attempts:
            print(f"\n🔄 开始第 {attempt_number} 轮重试...")
            print(f"📊 需要重试的链接: {len(error_links)} 个")
            
            clear_file(error_filename)
            error_links = extract_odds_only(
                error_links, output_filename, error_filename, 
                attempt_number, max_attempts, driver_type=driver_type, stealth_level=stealth_level,
                chromedriver_path=chromedriver_path, chrome_binary_path=chrome_binary_path
            )
            attempt_number += 1
        
        # 最终结果
        if not error_links:
            print(f"\n🎉 全部处理完成！")
        else:
            print(f"\n⚠️  仍有 {len(error_links)} 个链接失败")
            print(f"💾 失败链接保存在 {error_filename}")
        
        print(f"💾 成功结果保存在 {output_filename}")
        
    except KeyboardInterrupt:
        print("\n⏹️  用户中断操作")
    except Exception as e:
        print(f"\n❌ 程序异常: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("🔚 程序结束")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='简化版网球赔率爬虫 - 只需要href即可')
    parser.add_argument('--input', type=str, default="odds_scaped/input1.jsonl", help='输入jsonl文件路径（必须包含href字段）')
    parser.add_argument('--output', type=str, default="odds_scaped/output1.jsonl", help='输出文件路径（默认：input文件名_odds.jsonl）')
    parser.add_argument('--error', type=str, default="odds_scaped/error1.jsonl", help='错误文件路径（默认：input文件名_error.jsonl）')
    parser.add_argument('--driver_type', type=str, default='proxy1', 
                        choices=['local', 'proxy1', 'proxy2', 'proxy3', 'proxy4', 'proxy5'], help='驱动类型（默认：proxy1）')
    parser.add_argument('--stealth_level', type=str, default='minimal',
                        choices=['minimal', 'light', 'medium'], 
                        help='隐身级别（默认：light）')
    parser.add_argument('--chromedriver_path', type=str, default=None,
                        help='ChromeDriver path; defaults to CHROMEDRIVER_PATH or webdriver-manager')
    parser.add_argument('--chrome_binary_path', type=str, default=None,
                        help='Chrome binary path; defaults to CHROME_BINARY or system Chrome')
    
    args = parser.parse_args()
    
    # 自动生成output和error文件名
    input_filename = args.input
    
    if args.output:
        output_filename = args.output
    else:
        # input.jsonl -> input_odds.jsonl
        base_name = input_filename.replace('.jsonl', '')
        output_filename = f"{base_name}_odds.jsonl"
    
    if args.error:
        error_filename = args.error
    else:
        # input.jsonl -> input_error.jsonl
        base_name = input_filename.replace('.jsonl', '')
        error_filename = f"{base_name}_error.jsonl"
    
    print(f"🎾 简化版赔率爬虫")
    print(f"📂 输入文件: {input_filename}")
    print(f"📂 输出文件: {output_filename}")
    print(f"📂 错误文件: {error_filename}")
    print(f"📅 启动时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    start_time = time.time()
    main(input_filename, output_filename, error_filename, 
         driver_type=args.driver_type, stealth_level=args.stealth_level,
         chromedriver_path=args.chromedriver_path, chrome_binary_path=args.chrome_binary_path)
    end_time = time.time()
    
    print(f"⏱️  总耗时: {end_time - start_time:.2f} 秒")
    print(f"📅 结束时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")