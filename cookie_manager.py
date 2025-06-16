"""
Cookie管理模块
处理浏览器Cookie获取、文件验证和相关操作
"""

import os
import time
from config import BROWSER_CONFIG, COOKIE_CONFIG
from utils import validate_file_exists, get_browser_profile_path


class CookieManager:
    """Cookie管理器类"""
    
    def __init__(self):
        self.use_browser = True
        self.browser = 'firefox'
        self.cookie_file = None
        
    def set_browser_mode(self, browser_name):
        """
        设置浏览器模式
        
        Args:
            browser_name (str): 浏览器名称
        """
        self.use_browser = True
        browser_map = BROWSER_CONFIG['browser_map']
        self.browser = browser_map.get(browser_name, 'firefox')
        
    def set_file_mode(self, cookie_file_path):
        """
        设置文件模式
        
        Args:
            cookie_file_path (str): Cookie文件路径
        """
        self.use_browser = False
        self.cookie_file = cookie_file_path
        
    def get_cookie_args(self):
        """
        获取cookie相关的命令行参数
        
        Returns:
            list: Cookie参数列表
            
        Raises:
            Exception: 当配置无效时抛出异常
        """
        if self.use_browser:
            return self._get_browser_cookie_args()
        else:
            return self._get_file_cookie_args()
            
    def _get_browser_cookie_args(self):
        """获取浏览器Cookie参数"""
        # 验证浏览器配置文件目录
        appdata_local = os.getenv('LOCALAPPDATA')
        if not appdata_local:
            raise Exception("无法获取 LOCALAPPDATA 环境变量")
            
        profile_dir = get_browser_profile_path(self.browser, appdata_local)
        if not profile_dir or not os.path.exists(profile_dir):
            browser_names = {v: k for k, v in BROWSER_CONFIG['browser_map'].items()}
            browser_display_name = browser_names.get(self.browser, self.browser)
            raise Exception(f"找不到浏览器 {browser_display_name} 的配置文件目录: {profile_dir}")
            
        return ["--cookies-from-browser", self.browser]
        
    def _get_file_cookie_args(self):
        """获取文件Cookie参数"""
        if not self.cookie_file:
            raise Exception("未设置Cookie文件")
            
        validate_file_exists(self.cookie_file, "Cookie文件")
        
        # 规范化路径
        cookie_path = os.path.normpath(self.cookie_file)
        return ["--cookies", cookie_path]
        
    def validate_cookie_file(self, file_path):
        """
        验证cookie文件格式和内容
        
        Args:
            file_path (str): Cookie文件路径
            
        Returns:
            dict: 验证结果字典
        """
        result = {
            'is_valid': False,
            'issues': [],
            'youtube_cookies_count': 0,
            'important_cookies': [],
            'expired_cookies': 0,
            'total_cookies': 0
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            if not lines:
                result['issues'].append("文件为空")
                return result
                
            # 检查文件头
            first_line = lines[0].strip()
            valid_headers = COOKIE_CONFIG['cookie_file_headers']
            if not any(first_line.startswith(header) for header in valid_headers):
                result['issues'].append("文件头格式不正确")
                
            # 分析cookie内容
            important_cookies = COOKIE_CONFIG['important_cookies']
            current_time = int(time.time())
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                    
                # 解析cookie行
                parts = line.split('\t')
                if len(parts) < 7:
                    continue
                    
                result['total_cookies'] += 1
                domain, _, _, _, expiry, name, _ = parts[:7]
                
                # 检查YouTube相关cookie
                if 'youtube.com' in domain or '.youtube.com' in domain:
                    result['youtube_cookies_count'] += 1
                    
                # 检查重要cookie
                if name in important_cookies:
                    result['important_cookies'].append(name)
                    
                # 检查过期cookie
                try:
                    expiry_time = int(expiry)
                    if expiry_time != 0 and expiry_time < current_time:
                        result['expired_cookies'] += 1
                except ValueError:
                    pass
                    
            # 验证结果
            if result['total_cookies'] > 0 and result['youtube_cookies_count'] > 0:
                result['is_valid'] = True
                
            # 去重重要cookie列表
            result['important_cookies'] = list(set(result['important_cookies']))
            
        except Exception as e:
            result['issues'].append(f"读取文件时出错: {str(e)}")
            
        return result
        
    def get_cookie_suggestions(self, file_path):
        """
        获取Cookie文件问题的建议
        
        Args:
            file_path (str): Cookie文件路径
            
        Returns:
            list: 建议列表
        """
        suggestions = []
        
        try:
            validation_result = self.validate_cookie_file(file_path)
            
            if validation_result['total_cookies'] == 0:
                suggestions.append("文件中没有找到有效的Cookie")
                suggestions.append("请确保导出的是正确的cookies.txt文件")
                
            if validation_result['youtube_cookies_count'] == 0:
                suggestions.append("文件中没有YouTube相关的Cookie")
                suggestions.append("请确保在导出时选择了youtube.com域名")
                
            if not validation_result['important_cookies']:
                suggestions.append("缺少重要的认证Cookie")
                suggestions.append("请确保在YouTube上完全登录后再导出Cookie")
                
            if validation_result['expired_cookies'] > validation_result['total_cookies'] * 0.5:
                suggestions.append("大部分Cookie已过期")
                suggestions.append("请重新登录YouTube并导出新的Cookie文件")
                
        except Exception as e:
            suggestions.append(f"无法分析文件: {str(e)}")
            
        return suggestions
        
    def export_cookie_instructions(self):
        """
        获取Cookie导出说明
        
        Returns:
            str: 导出说明文本
        """
        return """
Cookie导出步骤：

1. 安装浏览器插件：
   - 推荐使用 'Get cookies.txt LOCALLY' 插件
   - Chrome: 在Chrome网上应用店搜索安装
   - Firefox: 在Firefox附加组件商店搜索安装

2. 登录YouTube：
   - 打开 https://www.youtube.com
   - 确保完全登录到您的账户

3. 导出Cookie：
   - 点击插件图标
   - 选择 'youtube.com' 域名
   - 点击 'Export' 导出
   - 保存为 cookies.txt 文件

4. 使用Cookie文件：
   - 在本程序中选择 '从文件获取' 模式
   - 浏览并选择刚才导出的 cookies.txt 文件

注意事项：
- Cookie文件包含敏感信息，请妥善保管
- 定期更新Cookie文件以保持有效性
- 不要与他人分享您的Cookie文件
        """
        
    def test_cookie_validity(self, progress_callback=None):
        """
        测试Cookie有效性
        
        Args:
            progress_callback (callable): 进度回调函数
            
        Returns:
            dict: 测试结果
        """
        result = {
            'success': False,
            'message': '',
            'details': []
        }
        
        try:
            if progress_callback:
                progress_callback("🔍 开始测试Cookie有效性...")
                
            # 构建测试命令
            from utils import build_yt_dlp_command, run_subprocess
            
            test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # 测试视频
            command = build_yt_dlp_command(
                base_args=["-J", "--no-warnings", "--no-playlist"],
                cookie_args=self.get_cookie_args(),
                url=test_url
            )
            
            if progress_callback:
                progress_callback("📡 正在连接YouTube...")
                
            # 执行测试
            process_result = run_subprocess(command, check=False)
            
            if process_result.returncode == 0:
                result['success'] = True
                result['message'] = "Cookie测试成功！可以正常访问YouTube"
                if progress_callback:
                    progress_callback("✅ Cookie测试成功")
            else:
                result['message'] = "Cookie测试失败"
                result['details'].append(f"错误代码: {process_result.returncode}")
                if process_result.stderr:
                    result['details'].append(f"错误信息: {process_result.stderr}")
                if progress_callback:
                    progress_callback("❌ Cookie测试失败")
                    
        except Exception as e:
            result['message'] = f"测试过程中出错: {str(e)}"
            if progress_callback:
                progress_callback(f"❌ 测试出错: {str(e)}")
                
        return result
