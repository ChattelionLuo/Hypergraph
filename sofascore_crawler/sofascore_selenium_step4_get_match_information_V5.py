import json
import os
import time
import random
import string
from selenium import webdriver
from seleniumwire import webdriver as seleniumwire_webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
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


def proxy_config_from_env(proxy_name):
    env_key = f"SOFASCORE_{proxy_name.upper()}_URL"
    proxy_url = os.environ.get(env_key) or os.environ.get("SOFASCORE_PROXY_URL")
    if not proxy_url:
        raise RuntimeError(
            f"Proxy driver {proxy_name!r} requires {env_key} or SOFASCORE_PROXY_URL"
        )
    return {"url": proxy_url}

class RealisticStealthConfig:
    """更现实的隐身配置 - 基于真实人类浏览行为"""
    
    # 优化后的隐身级别配置
    STEALTH_LEVELS = {
        'minimal': {
            'delays': {'min': 8, 'max': 18, 'jitter': 0.3},
            'behavior_frequency': 0.1,
            'mouse_movements': False,
            'random_clicks': False,
            'scroll_variety': False,
            'description': '快速测试模式'
        },
        'light': {
            'delays': {'min': 5, 'max': 15, 'jitter': 0.1},
            'behavior_frequency': 0.05,
            'mouse_movements': True,
            'random_clicks': False,
            'scroll_variety': True,
            'description': '正常浏览速度'
        },
        'medium': {
            'delays': {'min': 25, 'max': 50, 'jitter': 0.5},
            'behavior_frequency': 0.5,
            'mouse_movements': True,
            'random_clicks': True,
            'scroll_variety': True,
            'description': '仔细浏览模式'
        },
        'high': {
            'delays': {'min': 35, 'max': 80, 'jitter': 0.6},
            'behavior_frequency': 0.7,
            'mouse_movements': True,
            'random_clicks': True,
            'scroll_variety': True,
            'long_pauses': True,
            'description': '深度研究模式'
        },
        'ultra': {
            'delays': {'min': 45, 'max': 120, 'jitter': 0.8},
            'behavior_frequency': 0.9,
            'mouse_movements': True,
            'random_clicks': True,
            'scroll_variety': True,
            'long_pauses': True,
            'random_breaks': True,
            'description': '极度安全模式'
        }
    }
    
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ]
    
    LANGUAGES = [
        "en-US,en;q=0.9",
        "en-GB,en;q=0.9", 
        "en-US,en;q=0.9,zh;q=0.8",
        "en-US,en;q=0.9,es;q=0.8"
    ]

class RealisticStealthDriver:
    """基于真实人类行为的隐身驱动器"""
    
    def __init__(self, proxy_config=None, stealth_level="light"):
        self.proxy_config = proxy_config
        self.config = RealisticStealthConfig.STEALTH_LEVELS[stealth_level]
        self.stealth_level = stealth_level
        self.user_agent = random.choice(RealisticStealthConfig.USER_AGENTS)
        self.language = random.choice(RealisticStealthConfig.LANGUAGES)
        
    def create_driver(self):
        """创建基于真实行为的隐身驱动"""
        options = self._create_realistic_options()
        service = chrome_service()
        
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
        
        driver.set_page_load_timeout(45)  # 更长的超时
        driver.implicitly_wait(10)
        
        return driver
    
    def _create_realistic_options(self):
        """创建更真实的Chrome选项"""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        # 核心隐身选项
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument(f'--user-agent={self.user_agent}')
        options.add_argument(f'--lang={self.language.split(",")[0]}')
        
        # 性能优化但保持真实性
        options.add_argument('--disable-images')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-extensions')
        options.add_argument('--no-first-run')
        
        # 内存优化
        options.add_argument('--memory-pressure-off')
        options.add_argument('--disable-background-timer-throttling')
        
        apply_chrome_binary(options)
        return options
    
    def _setup_proxy(self):
        """设置代理配置"""
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
        """智能请求拦截器 - 修复版本"""
        def interceptor(request):
            # 阻止明显的追踪器
            block_domains = [
                'google-analytics.com', 'googletagmanager.com', 
                'googlesyndication.com', 'doubleclick.net',
                'facebook.com', 'twitter.com', 'adnxs.com',
                'amazon-adsystem.com', 'scorecardresearch.com'
            ]
            
            if any(domain in request.url.lower() for domain in block_domains):
                request.abort()
                return
            
            # 修复：逐个设置请求头，而不是使用 update()
            try:
                # 基础浏览器头部
                request.headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
                request.headers['Accept-Language'] = self.language
                request.headers['Accept-Encoding'] = 'gzip, deflate, br'
                request.headers['Connection'] = 'keep-alive'
                request.headers['Upgrade-Insecure-Requests'] = '1'
                
                # 现代浏览器安全头部
                request.headers['Sec-Fetch-Dest'] = 'document'
                request.headers['Sec-Fetch-Mode'] = 'navigate'
                request.headers['Sec-Fetch-Site'] = 'none'
                
                # 随机添加一些headers
                if random.random() < 0.4:
                    request.headers['Cache-Control'] = 'no-cache'
                
                if random.random() < 0.3:
                    request.headers['DNT'] = '1'  # Do Not Track
                    
                # 偶尔添加其他真实头部
                if random.random() < 0.2:
                    request.headers['Sec-Fetch-User'] = '?1'
                    
            except Exception as e:
                # 如果设置头部失败，继续执行但记录警告
                print(f"⚠️  设置请求头失败: {e}")
    
        return interceptor
    
    def _execute_stealth_scripts(self, driver):
        """执行隐身脚本"""
        stealth_scripts = [
            # 隐藏webdriver
            """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            """,
            
            # 伪造plugins
            """
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            """,
            
            # Chrome对象
            """
            window.chrome = {
                runtime: {},
                app: {
                    isInstalled: false,
                },
            };
            """,
            
            # 权限API
            """
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
            );
            """
        ]
        
        for script in stealth_scripts:
            try:
                driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                    'source': script
                })
            except:
                try:
                    driver.execute_script(script)
                except:
                    pass

class RealisticBehavior:
    """基于真实人类行为的模拟器"""
    
    def __init__(self, driver, config, stealth_level):
        self.driver = driver
        self.config = config
        self.stealth_level = stealth_level
        self.actions = ActionChains(driver)
    
    def smart_delay(self, base_min=None, base_max=None, context="normal"):
        """智能延迟 - 基于上下文调整"""
        if base_min is None:
            base_min = self.config['delays']['min']
        if base_max is None:
            base_max = self.config['delays']['max']
        
        # 根据上下文调整延迟
        if context == "page_load":
            base_min *= 0.8  # 页面加载稍快
            base_max *= 0.8
        elif context == "data_extraction":
            base_min *= 0.5  # 数据提取更快
            base_max *= 0.6
        elif context == "between_links":
            # 链接间延迟保持原始配置
            pass
        
        base_delay = random.uniform(base_min, base_max)
        jitter = random.uniform(-self.config['delays']['jitter'], self.config['delays']['jitter']) * base_delay
        
        final_delay = max(1, base_delay + jitter)
        
        # 偶尔添加额外长暂停（模拟分心/思考）
        if (self.config.get('long_pauses', False) and 
            random.random() < 0.1):  # 10%概率
            extra_pause = random.uniform(20, 30)
            final_delay += extra_pause
            print(f"  🤔 模拟长时间思考: +{extra_pause:.1f}秒")
        
        print(f"  ⏳ 等待 {final_delay:.1f} 秒...")
        time.sleep(final_delay)
    
    def conditional_behavior(self, behavior_func):
        """条件性执行行为"""
        if random.random() < self.config['behavior_frequency']:
            behavior_func()
    
    def realistic_scroll(self):
        """真实的滚动行为"""
        if self.config['scroll_variety']:
            # 多种滚动模式
            scroll_type = random.choice(['smooth', 'quick', 'hesitant'])
            
            if scroll_type == 'smooth':
                # 平滑滚动
                for _ in range(random.randint(2, 4)):
                    scroll_amount = random.randint(150, 400)
                    self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                    time.sleep(random.uniform(0.3, 0.8))
            
            elif scroll_type == 'quick':
                # 快速滚动
                scroll_amount = random.randint(400, 800)
                self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                time.sleep(random.uniform(0.2, 0.5))
            
            else:  # hesitant
                # 犹豫式滚动（上下滚动）
                down_scroll = random.randint(200, 500)
                self.driver.execute_script(f"window.scrollBy(0, {down_scroll});")
                time.sleep(random.uniform(0.5, 1.2))
                up_scroll = random.randint(50, 150)
                self.driver.execute_script(f"window.scrollBy(0, -{up_scroll});")
                time.sleep(random.uniform(0.3, 0.8))
        else:
            # 简单滚动
            scroll_amount = random.randint(200, 400)
            self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            time.sleep(random.uniform(0.4, 1.0))
    
    def natural_mouse_movement(self):
        """自然鼠标移动"""
        if self.config['mouse_movements']:
            try:
                # 获取窗口大小
                window_size = self.driver.get_window_size()
                width = window_size['width']
                height = window_size['height']
                
                # 模拟自然鼠标轨迹
                for _ in range(random.randint(2, 4)):
                    x_offset = random.randint(-200, 200)
                    y_offset = random.randint(-200, 200)
                    
                    self.actions.move_by_offset(x_offset, y_offset).perform()
                    time.sleep(random.uniform(0.1, 0.3))
                
                # 重置actions
                self.actions = ActionChains(self.driver)
            except Exception:
                pass
    
    def random_break(self):
        """随机休息（模拟人类暂停行为）"""
        if (self.config.get('random_breaks', False) and 
            random.random() < 0.05):  # 5%概率
            break_time = random.uniform(30, 120)
            print(f"  ☕ 模拟随机休息: {break_time:.1f}秒")
            time.sleep(break_time)

# 创建优化的驱动函数
def create_realistic_proxy1_driver(stealth_level="light"):
    proxy_config = proxy_config_from_env("proxy1")
    stealth_driver = RealisticStealthDriver(proxy_config, stealth_level)
    return stealth_driver.create_driver()

def create_realistic_proxy2_driver(stealth_level="light"):
    proxy_config = proxy_config_from_env("proxy2")
    stealth_driver = RealisticStealthDriver(proxy_config, stealth_level)
    return stealth_driver.create_driver()

def create_realistic_proxy3_driver(stealth_level="light"):
    proxy_config = proxy_config_from_env("proxy3")
    stealth_driver = RealisticStealthDriver(proxy_config, stealth_level)
    return stealth_driver.create_driver()

def create_realistic_local_driver(stealth_level="minimal"):
    stealth_driver = RealisticStealthDriver(None, stealth_level)
    return stealth_driver.create_driver()

def realistic_process_links(input_links, output_filename, error_filename, 
                          attempt_number=1, max_attempts=2, driver_type='local', stealth_level='light'):
    """基于真实人类行为的链接处理函数 - 完整版本"""
    
    fout = open(output_filename, "a", encoding="utf-8")
    ferror = open(error_filename, "a", encoding="utf-8")
    error_links = []
    
    # 获取配置
    config = RealisticStealthConfig.STEALTH_LEVELS[stealth_level]
    
    print(f"\n========== 第 {attempt_number} 轮处理开始 ==========")
    print(f"🔒 隐身级别: {stealth_level} - {config['description']}")
    print(f"📊 待处理链接: {len(input_links)} 个")
    
    # 预估时间
    avg_delay = (config['delays']['min'] + config['delays']['max']) / 2
    estimated_hours = (len(input_links) * avg_delay) / 3600
    
    if estimated_hours < 1:
        time_str = f"{estimated_hours * 60:.0f}分钟"
    else:
        time_str = f"{estimated_hours:.1f}小时"
    
    print(f"⏰ 预估完成时间: {time_str}")
    print(f"💡 建议: 延迟范围 {config['delays']['min']}-{config['delays']['max']}秒")
    
    for idx, linkinfo in enumerate(input_links):
        url = linkinfo["href"]
        ATP_competition = linkinfo["ATP_competition"]
        year = linkinfo["year"]
        date = linkinfo["date"]
        conditions = linkinfo["conditions"]
        error_message = 'None'
        
        if conditions != "FT":
            print(f"⏭️  跳过非FT链接：{ATP_competition} {year} {date} {conditions}")
            continue
            
        if date == "error":
            print(f"⚠️  跳过错误链接：{ATP_competition} {year} {date}")
            success = False
        else:
            print(f"\n📍 ({idx+1}/{len(input_links)}) 开始处理: {ATP_competition} {year}")
            success = False
            
            driver = None
            behavior = None
            
            try:
                # 创建驱动
                if driver_type == 'proxy1':
                    driver = create_realistic_proxy1_driver(stealth_level)
                elif driver_type == 'proxy2':
                    driver = create_realistic_proxy2_driver(stealth_level)
                elif driver_type == 'proxy3':
                    driver = create_realistic_proxy3_driver(stealth_level)
                else:
                    driver = create_realistic_local_driver(stealth_level)
                
                behavior = RealisticBehavior(driver, config, stealth_level)
                
                print(f"🌐 ChromeDriver启动成功，端口: {driver.service.port}")
                
                # 链接间的主要延迟
                behavior.smart_delay(context="between_links")
                
                # 访问URL
                driver.get(url)
                print(f"✅ 页面访问成功: {url}")
                
                # 页面加载后的短暂延迟
                behavior.smart_delay(context="page_load")
                
                # 等待主要内容
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.md\\:br_lg.mx_auto"))
                )
                
                # 模拟人类浏览行为
                behavior.conditional_behavior(behavior.realistic_scroll)
                behavior.conditional_behavior(behavior.natural_mouse_movement)
                
                main_div = driver.find_element(By.CSS_SELECTOR, "div.md\\:br_lg.mx_auto")
                
                # ============ 开始完整的数据提取 ============
                print("📊 开始提取基础信息...")
                
                # 1. 获取球员链接和信息
                WebDriverWait(main_div, 25).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "a[href^='/team/tennis/']"))
                )
                
                player_a_tags = main_div.find_elements(By.CSS_SELECTOR, "a[href^='/team/tennis/']")
                player_links = [a.get_attribute("href") for a in player_a_tags]
                
                # 球员名字
                player_names = []
                for a in player_a_tags:
                    try:
                        bdi = a.find_element(By.TAG_NAME, "bdi")
                        player_names.append(bdi.text.strip())
                    except Exception:
                        player_names.append("")
                    
                    # 轻微延迟模拟人类提取行为
                    # behavior.smart_delay(0.1, 0.3, context="data_extraction")
                
                print(f"👥 球员: {player_names}")
                
                # 球员状态（Q等）
                player_conditions = []
                for a in player_a_tags:
                    try:
                        cond = a.find_element(By.XPATH, ".//span[contains(@class, 'textStyle_assistive') and contains(@class, 'micro') and contains(@class, 'c_surface') and contains(@class, 's1') and contains(@class, 'lh_1')]")
                        player_conditions.append(cond.text.strip())
                    except Exception:
                        player_conditions.append(None)
                
                # 2. 比分提取
                print("🎾 提取比分信息...")
                behavior.conditional_behavior(behavior.realistic_scroll)
                
                score_flex = main_div.find_element(
                    By.XPATH, ".//div[contains(@class, 'd_flex') and contains(@class, 'ai_center') and contains(@class, 'jc_center') and contains(@class, 'flex-d_column') and contains(@class, 'w_100%')]"
                )
                
                set_score_boxes = score_flex.find_elements(
                    By.XPATH,
                    ".//div[contains(@class, 'd_flex') and contains(@class, 'flex-d_column') and contains(@class, 'ai_flex-end') and contains(@class, 'jc_space-between') and contains(@class, 'py_xs')]"
                )
                final_score_boxes = score_flex.find_element(
                    By.XPATH,
                    ".//div[contains(@class, 'd_flex') and contains(@class, 'flex-d_column') and contains(@class, 'jc_space-between') and contains(@class, 'h_100%') and contains(@class, 'gap_2xl')]"
                )
                
                player1_score, player2_score = [], []
                for i, box in enumerate(set_score_boxes):
                    try:
                        score = box.find_elements(By.XPATH, ".//span[contains(@class, 'Text') and contains(@class, 'currentScore')]")
                        score = [s.text.strip() for s in score]
                        player1_score.append(score[0])
                        player2_score.append(score[1])
                    except Exception:
                        pass
                
                final_score = final_score_boxes.find_elements(By.XPATH, ".//span[contains(@class, 'Text') and contains(@class, 'currentScore')]")
                final_score = [s.text.strip() for s in final_score]
                player1_score.append(final_score[0])
                player2_score.append(final_score[1])
                
                print(f"📊 比分: {player1_score} vs {player2_score}")
                
                # 3. 切换到Details页面
                print("📋 切换到Details页面...")
                behavior.conditional_behavior(behavior.realistic_scroll)
                behavior.smart_delay(0.5, 1, context="data_extraction")
                
                details_button = WebDriverWait(driver, 25).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'h2[data-tabid="details"]'))
                )
                
                # 模拟移动到按钮
                behavior.conditional_behavior(lambda: behavior.actions.move_to_element(details_button).perform())
                behavior.smart_delay(0.2, 0.8, context="data_extraction")
                
                driver.execute_script("arguments[0].click();", details_button)
                # behavior.smart_delay(0.5, 1.5, context="data_extraction")
                # behavior.conditional_behavior(behavior.realistic_scroll)
                
                # 等待Details页面加载
                main_div = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-panelid='details'].TabPanel.bpHovE"))
                )
                
                # 4. 提取赔率信息
                print("💰 提取赔率信息...")
                try:
                    odds_div = main_div.find_element(By.CSS_SELECTOR, "div.d_flex.jc_space-between.gap_sm.pb_sm")
                    odds_spans = odds_div.find_elements(By.XPATH, ".//span[contains(@class, 'textStyle_display.micro') and contains(@class, 'c_neutrals.nLv1')]")
                    odds = [span.text.strip() for span in odds_spans]
                    print(f"💰 赔率: {odds}")
                except Exception:
                    odds = ['not found', 'not found']
                    print("💰 赔率信息未找到")
                
                # 5. 提取时间信息
                print("⏰ 提取时间信息...")
                # behavior.smart_delay(0.5, 1.0, context="data_extraction")
                
                settime_spans = main_div.find_elements(
                    By.XPATH,
                    ".//span[contains(@class, 'textStyle_display') and contains(@class, 'small') and contains(@class, 'c_neutrals') and contains(@class, 'nLv1') and contains(@class, 'lh_100%') and contains(@class, 'ta_center') and contains(@class, 'd_block')]"
                )
                settime = [span.text.strip() for span in settime_spans if span.text.strip() != ""]
                print(f"⏰ 时间信息: {settime}")
                
                # 6. 提取其他详细信息
                print("📝 提取其他详细信息...")
                others = []
                others_div = main_div.find_elements(
                    By.XPATH,
                    ".//div[contains(@class, 'd_flex') and contains(@class, 'ai_center') and contains(@class, 'gap_sm') and contains(@class, 'px_lg') and contains(@class, 'py_sm')]"
                )
                
                for i, box in enumerate(others_div):
                    try:
                        others_item = box.find_element(By.XPATH, ".//span[contains(@class, 'textStyle_body.medium') and contains(@class, 'c_neutrals.nLv1') and contains(@class, 'ov_hidden')]").text.strip()
                        others.append(others_item)
                    except Exception:
                        pass
                    # behavior.smart_delay(0.1, 0.3, context="data_extraction")
                
                print(f"📝 其他信息: {others}")
                
                # 7. 统计信息获取（根据隐身级别决定）
                statistics_keys = []
                statistics_values = []
                
                print("📈 提取统计信息...")
                try:
                    # 人类行为模拟
                    # behavior.conditional_behavior(behavior.realistic_scroll)
                    # behavior.smart_delay(0.3, 1.2, context="data_extraction")
                    
                    statistics_button = WebDriverWait(driver, 35).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, 'h2[data-tabid="statistics"]'))
                    )
                    
                    # 移动并点击统计按钮
                    # behavior.conditional_behavior(lambda: behavior.actions.move_to_element(statistics_button).perform())
                    behavior.smart_delay(0.5, 1, context="data_extraction")

                    driver.execute_script("arguments[0].click();", statistics_button)
                    # behavior.smart_delay(2, 4, context="data_extraction")
                    
                    # behavior.conditional_behavior(behavior.realistic_scroll)
                    
                    # 等待统计页面加载
                    main_div = WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-panelid='statistics'].TabPanel.bpHovE"))
                    )
                    
                    # 提取统计数据
                    statistics_div = WebDriverWait(main_div, 25).until(
                        EC.presence_of_all_elements_located((By.XPATH, ".//div[contains(@class, 'mdDown:pos_relative') and contains(@class, 'mdDown:br_lg') and contains(@class, 'mdDown:bg_surface.s1') and contains(@class, 'mdDown:elevation_2') and contains(@class, 'md:pos_relative') and contains(@class, 'md:br_sm') and contains(@class, 'md:bg_surface.s2') and contains(@class, 'md:elevation_none')]"))
                    )
                    
                    print(f"📊 找到 {len(statistics_div)} 个统计分类")
                    
                    for row_idx, row in enumerate(statistics_div):
                        try:
                            main_class = row.find_element(By.XPATH, ".//div[contains(@class, 'd_block') and contains(@class, 'md:d_block')]")
                            main_class_name = main_class.find_element(By.CSS_SELECTOR, "span")
                            
                            feature_name = row.find_elements(By.CSS_SELECTOR, "span.Text.lluFbU")
                            player1_value = row.find_elements(By.CSS_SELECTOR, "span.Text.iZtpCa")
                            player2_value = row.find_elements(By.CSS_SELECTOR, "span.Text.lfzhVF")
                            
                            for i in range(len(feature_name)):
                                statistics_keys.append('player1_' + main_class_name.text + '_' + feature_name[i].text)
                                statistics_keys.append('player2_' + main_class_name.text + '_' + feature_name[i].text)
                                statistics_values.append(player1_value[i].text)
                                statistics_values.append(player2_value[i].text)
                            
                            # 在处理统计行之间添加人类行为
                            # behavior.smart_delay(0.2, 0.5, context="data_extraction")
                            
                        except Exception as e:
                            print(f"⚠️  统计数据行 {row_idx} 处理失败: {e}")
                            continue
                    
                    print(f"📊 成功提取 {len(statistics_keys)} 个统计指标")
                    
                except Exception as e1:
                    error_message = f"统计信息获取失败: {e1}"
                    print(f"统计信息获取失败")
                
                
                
                # 8. 构建最终记录
                print("💾 构建数据记录...")
                record = {
                    "ATP_competition": ATP_competition,
                    "year": year,
                    "date": date,
                    "conditions": conditions,
                    "href": url,
                    "player1_link": player_links[0] if len(player_links) > 0 else "",
                    "player2_link": player_links[1] if len(player_links) > 1 else "",
                    "player1_name": player_names[0] if len(player_names) > 0 else "",
                    "player2_name": player_names[1] if len(player_names) > 1 else "",
                    "player1_conditions": player_conditions[0] if len(player_conditions) > 0 else None,
                    "player2_conditions": player_conditions[1] if len(player_conditions) > 1 else None,
                    "player1_score": player1_score,
                    "player2_score": player2_score,
                    'player1_odds': odds[0] if len(odds) > 0 else "",
                    'player2_odds': odds[1] if len(odds) > 1 else "",
                    "set_time": settime,
                    "Date and time": others[0] if len(others) > 0 else "",
                    "Competition": others[1] if len(others) > 1 else "",
                    "Venue": others[2] if len(others) > 2 else "",
                    "Location": others[3] if len(others) > 3 else "",
                    "Ground type": others[4] if len(others) > 4 else "",
                }
                
                # 添加统计数据
                record.update({key: value for key, value in zip(statistics_keys, statistics_values)})
                
                # 保存记录
                fout.write(json.dumps(record, ensure_ascii=False) + "\n")
                fout.flush()
                
                print(f"✅ 成功完成: {ATP_competition} {year} {date}")
                print(f"📊 数据字段: {len(record)} 个")
                success = True
                
                # 随机休息
                behavior.random_break()
                
            except TimeoutException as e:
                print(f"⏰ 超时失败: {ATP_competition} {year} {date} - {e}")
                error_message = error_message+f"Timeout: {str(e)}"
                
            except Exception as e:
                print(f"❌ 异常失败: {ATP_competition} {year} {date} - {e}")
                error_message = error_message+ f"Error: {str(e)}"
                
            finally:
                if driver:
                    try:
                        driver.quit()
                        print("🔒 浏览器已关闭")
                    except Exception as quit_error:
                        print(f"⚠️  浏览器关闭异常: {quit_error}")
        
        if not success:
            print(f"💔 处理失败: {ATP_competition} {year}")
            error_record = {
                "ATP_competition": ATP_competition,
                "year": year, 
                "date": date,
                "conditions": conditions,
                "href": url,
                "player1_link": 'error',
                "player2_link": 'error',
                "attempt_number": attempt_number,
                "error_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "error_message": error_message
            }
            
            fout.write(json.dumps(error_record, ensure_ascii=False) + "\n")
            ferror.write(json.dumps(linkinfo, ensure_ascii=False) + "\n")
            fout.flush()
            ferror.flush()
            error_links.append(linkinfo)
            
            # 失败后延迟
            failure_delay = config['delays']['max'] * 2
            print(f"😴 失败后等待 {failure_delay:.1f} 秒...")
            time.sleep(failure_delay)
    
    fout.close()
    ferror.close()
    return error_links

# 辅助函数
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
        print(f"❌ 文件 {filename} 不存在")
    return links

def clear_file(filename):
    """清空文件内容"""
    with open(filename, "w", encoding="utf-8") as f:
        pass

# 主函数
def main(input_filename, output_filename, error_filename, driver_type='local', stealth_level='light'):
    """主函数 - 完整版本"""
    max_attempts = 3
    
    # 显示配置信息
    config = RealisticStealthConfig.STEALTH_LEVELS[stealth_level]
    print(f"🚀 真实人类行为爬虫启动")
    print(f"🔒 隐身级别: {stealth_level.upper()} ({config['description']})")
    print(f"⏱️  延迟范围: {config['delays']['min']}-{config['delays']['max']}秒 (jitter: {config['delays']['jitter']})")
    print(f"🌐 驱动类型: {driver_type}")
    print(f"📈 行为频率: {config['behavior_frequency']*100:.0f}%")
    
    # 显示功能开关
    features = []
    if config.get('mouse_movements'): features.append("鼠标移动")
    if config.get('random_clicks'): features.append("随机点击") 
    if config.get('scroll_variety'): features.append("多样滚动")
    if config.get('long_pauses'): features.append("长暂停")
    if config.get('random_breaks'): features.append("随机休息")
    
    print(f"🎛️  启用功能: {', '.join(features) if features else '基础模式'}")
    
    try:
        input_links = load_links_from_file(input_filename)
        
        if not input_links:
            print(f"❌ 输入文件 {input_filename} 为空或不存在")
            return
        
        print(f"📂 成功加载 {len(input_links)} 个链接")
        
        clear_file(error_filename)
        
        error_links = realistic_process_links(
            input_links, output_filename, error_filename, 
            1, max_attempts, driver_type=driver_type, stealth_level=stealth_level
        )
        
        # 重试逻辑
        attempt_number = 2
        while error_links and attempt_number <= max_attempts:
            print(f"\n🔄 开始第 {attempt_number} 轮重试...")
            print(f"📊 需要重试的链接: {len(error_links)} 个")
            
            clear_file(error_filename)
            error_links = realistic_process_links(
                error_links, output_filename, error_filename, 
                attempt_number, max_attempts, driver_type=driver_type, stealth_level=stealth_level
            )
            attempt_number += 1
        
        # 最终结果统计
        if not error_links:
            print(f"\n🎉 全部处理完成！")
            print(f"✅ 所有链接都已成功处理")
        else:
            print(f"\n⚠️  处理结束")
            print(f"📊 达到最大重试次数 ({max_attempts})，仍有 {len(error_links)} 个链接失败")
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
    parser = argparse.ArgumentParser(description='基于真实人类行为的网球数据爬虫 - 完整版')
    parser.add_argument('--input', help='Input JSONL with SofaScore match links')
    parser.add_argument('--output', help='Output JSONL for match information')
    parser.add_argument('--error', help='Error JSONL for failed links')
    parser.add_argument('--input_ATP', default='US_Open', help='赛事名称')
    parser.add_argument('--year', type=int, default=2020, help='年份')
    parser.add_argument('--driver_type', type=str, default='proxy1', 
                        choices=['local', 'proxy1', 'proxy2', 'proxy3'], help='驱动类型')
    parser.add_argument('--stealth_level', type=str, default='light',
                        choices=['minimal', 'light', 'medium', 'high', 'ultra'], 
                        help='隐身级别 (minimal最快, ultra最安全)')
    
    args = parser.parse_args()
    
    if args.input:
        input_filename = args.input
        output_filename = args.output or "match_information.jsonl"
        error_filename = args.error or "match_information_error.jsonl"
    else:
        input_filename = f"filtered_grand_slam_2016_2025_ft_splits/{args.input_ATP}_{args.year}.jsonl"
        output_filename = f"filtered_grand_slam_2016_2025_ft_splits/{args.input_ATP}_{args.year}_match_information.jsonl"
        error_filename = f"filtered_grand_slam_2016_2025_ft_splits/{args.input_ATP}_{args.year}_step4_error.jsonl"
    
    print(f"🎾 真实行为网球爬虫 - 完整版")
    print(f"🏆 赛事: {args.input_ATP} {args.year}")
    print(f"🔧 配置: {args.driver_type} + {args.stealth_level}")
    print(f"📅 启动时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    start_time = time.time()
    main(input_filename, output_filename, error_filename, 
         driver_type=args.driver_type, stealth_level=args.stealth_level)
    end_time = time.time()
    
    print(f"⏱️  总耗时: {end_time - start_time:.2f} 秒")
    print(f"📅 结束时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")