"""
配置管理器
简化配置选项的处理和管理
"""

import os
import json
from datetime import datetime
from config import DEFAULT_DOWNLOAD_DIR, QUALITY_CONFIG, BROWSER_CONFIG


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file="ytd_config.json"):
        self.config_file = config_file
        self.config = self._load_default_config()
        self.load_config()
        
    def _load_default_config(self):
        """加载默认配置"""
        return {
            'download': {
                'directory': DEFAULT_DOWNLOAD_DIR,
                'output_template': '',
                'use_archive': False,
                'archive_file': '',
                'quality': '1080p',
                'format_type': '自动选择',
                'audio_codec': '最佳',
                'custom_format': '248+251'
            },
            'cookie': {
                'use_browser': True,
                'browser': 'Firefox',
                'cookie_file': ''
            },
            'ui': {
                'auto_scroll_log': True,
                'show_progress': True,
                'window_geometry': None
            },
            'advanced': {
                'retry_count': 3,
                'socket_timeout': 30,
                'delay_between_downloads': 5
            }
        }
        
    def load_config(self):
        """从文件加载配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    self._merge_config(saved_config)
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            
    def save_config(self):
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            
    def _merge_config(self, saved_config):
        """合并保存的配置"""
        for section, values in saved_config.items():
            if section in self.config:
                if isinstance(values, dict):
                    self.config[section].update(values)
                else:
                    self.config[section] = values
                    
    def get_download_options(self):
        """获取下载选项"""
        return self.config['download'].copy()
        
    def set_download_options(self, **options):
        """设置下载选项"""
        for key, value in options.items():
            if key in self.config['download']:
                self.config['download'][key] = value
                
    def get_cookie_options(self):
        """获取Cookie选项"""
        return self.config['cookie'].copy()
        
    def set_cookie_options(self, **options):
        """设置Cookie选项"""
        for key, value in options.items():
            if key in self.config['cookie']:
                self.config['cookie'][key] = value
                
    def get_ui_options(self):
        """获取UI选项"""
        return self.config['ui'].copy()
        
    def set_ui_options(self, **options):
        """设置UI选项"""
        for key, value in options.items():
            if key in self.config['ui']:
                self.config['ui'][key] = value
                
    def get_advanced_options(self):
        """获取高级选项"""
        return self.config['advanced'].copy()
        
    def set_advanced_options(self, **options):
        """设置高级选项"""
        for key, value in options.items():
            if key in self.config['advanced']:
                self.config['advanced'][key] = value
                
    def get_all_options(self):
        """获取所有选项的扁平化字典"""
        options = {}
        for section_name, section_config in self.config.items():
            if isinstance(section_config, dict):
                for key, value in section_config.items():
                    options[key] = value
            else:
                options[section_name] = section_config
        return options
        
    def reset_to_defaults(self):
        """重置为默认配置"""
        self.config = self._load_default_config()
        
    def export_config(self, file_path):
        """导出配置到指定文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"导出配置失败: {e}")
            return False
            
    def import_config(self, file_path):
        """从指定文件导入配置"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
                self._merge_config(imported_config)
            return True
        except Exception as e:
            print(f"导入配置失败: {e}")
            return False


class OptionsBuilder:
    """选项构建器"""
    
    def __init__(self, config_manager=None):
        self.config_manager = config_manager or ConfigManager()
        self.options = {}
        
    def from_ui_components(self, url_group, mode_group, quality_group, 
                          cookie_group, output_group):
        """从UI组件构建选项"""
        # URL
        self.options['url'] = url_group.get_url()
        
        # 模式选项
        self.options['mode'] = mode_group.get_mode()
        self.options.update(mode_group.get_mode_options())
        
        # 质量选项
        self.options.update(quality_group.get_quality_options())
        
        # Cookie选项
        self.options.update(cookie_group.get_cookie_options())
        
        # 输出选项
        self.options.update(output_group.get_output_options())
        
        return self
        
    def with_defaults(self):
        """使用默认配置填充缺失的选项"""
        defaults = self.config_manager.get_all_options()
        for key, value in defaults.items():
            if key not in self.options:
                self.options[key] = value
        return self
        
    def validate(self):
        """验证选项"""
        from command_builder import OptionsValidator
        errors = OptionsValidator.validate_all_options(self.options)
        if errors:
            raise ValueError("选项验证失败: " + "; ".join(errors))
        return self
        
    def build(self):
        """构建最终选项"""
        return self.options.copy()


class PresetManager:
    """预设管理器"""
    
    def __init__(self, config_manager=None):
        self.config_manager = config_manager or ConfigManager()
        self.presets = self._load_default_presets()
        
    def _load_default_presets(self):
        """加载默认预设"""
        return {
            'high_quality': {
                'name': '高质量下载',
                'description': '最佳质量，MP4格式',
                'options': {
                    'format_choice': '最佳质量',
                    'format_type': 'MP4 (H.264)',
                    'audio_codec': 'AAC'
                }
            },
            'fast_download': {
                'name': '快速下载',
                'description': '720p，自动格式',
                'options': {
                    'format_choice': '720p',
                    'format_type': '自动选择',
                    'audio_codec': '最佳'
                }
            },
            'audio_only': {
                'name': '仅音频',
                'description': '最佳音频质量',
                'options': {
                    'format_choice': '最佳质量',
                    'format_type': '仅音频',
                    'audio_codec': 'Opus'
                }
            },
            'mobile_friendly': {
                'name': '移动设备友好',
                'description': '480p MP4格式',
                'options': {
                    'format_choice': '480p',
                    'format_type': 'MP4 (H.264)',
                    'audio_codec': 'AAC'
                }
            }
        }
        
    def get_preset_names(self):
        """获取预设名称列表"""
        return [preset['name'] for preset in self.presets.values()]
        
    def get_preset(self, preset_id):
        """获取指定预设"""
        return self.presets.get(preset_id, {}).get('options', {})
        
    def apply_preset(self, preset_id, base_options=None):
        """应用预设到选项"""
        preset_options = self.get_preset(preset_id)
        if base_options:
            result = base_options.copy()
            result.update(preset_options)
            return result
        return preset_options.copy()
        
    def save_custom_preset(self, preset_id, name, description, options):
        """保存自定义预设"""
        self.presets[preset_id] = {
            'name': name,
            'description': description,
            'options': options.copy(),
            'custom': True,
            'created_at': datetime.now().isoformat()
        }
        
    def delete_preset(self, preset_id):
        """删除预设"""
        if preset_id in self.presets and self.presets[preset_id].get('custom'):
            del self.presets[preset_id]
            return True
        return False


class SessionManager:
    """会话管理器"""
    
    def __init__(self):
        self.session_data = {
            'start_time': None,
            'downloads': [],
            'total_size': 0,
            'total_time': 0,
            'errors': []
        }
        
    def start_session(self):
        """开始会话"""
        self.session_data['start_time'] = datetime.now()
        self.session_data['downloads'] = []
        self.session_data['total_size'] = 0
        self.session_data['total_time'] = 0
        self.session_data['errors'] = []
        
    def add_download(self, url, title, size=0, duration=0, status='completed'):
        """添加下载记录"""
        download_record = {
            'url': url,
            'title': title,
            'size': size,
            'duration': duration,
            'status': status,
            'timestamp': datetime.now().isoformat()
        }
        self.session_data['downloads'].append(download_record)
        
        if status == 'completed':
            self.session_data['total_size'] += size
            self.session_data['total_time'] += duration
            
    def add_error(self, error_msg, context=None):
        """添加错误记录"""
        error_record = {
            'message': error_msg,
            'context': context,
            'timestamp': datetime.now().isoformat()
        }
        self.session_data['errors'].append(error_record)
        
    def get_session_summary(self):
        """获取会话摘要"""
        if not self.session_data['start_time']:
            return None
            
        total_downloads = len([d for d in self.session_data['downloads'] 
                             if d['status'] == 'completed'])
        failed_downloads = len([d for d in self.session_data['downloads'] 
                              if d['status'] == 'failed'])
        
        session_duration = (datetime.now() - self.session_data['start_time']).total_seconds()
        
        return {
            'session_duration': session_duration,
            'total_downloads': total_downloads,
            'failed_downloads': failed_downloads,
            'total_size': self.session_data['total_size'],
            'total_time': self.session_data['total_time'],
            'error_count': len(self.session_data['errors']),
            'average_speed': (self.session_data['total_size'] / session_duration 
                            if session_duration > 0 else 0)
        }
        
    def export_session_log(self, file_path):
        """导出会话日志"""
        try:
            log_data = {
                'session_info': self.get_session_summary(),
                'downloads': self.session_data['downloads'],
                'errors': self.session_data['errors']
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"导出会话日志失败: {e}")
            return False
