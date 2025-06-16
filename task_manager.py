"""
任务管理器
提供异步任务执行和UI响应优化
"""

import threading
import queue
import time
from PyQt5.QtCore import QObject, QThread, pyqtSignal as Signal, QTimer


class TaskWorker(QThread):
    """任务工作线程"""
    
    task_completed = Signal(object)  # 任务完成信号
    task_error = Signal(str)         # 任务错误信号
    task_progress = Signal(str)      # 任务进度信号
    
    def __init__(self):
        super().__init__()
        self.task_queue = queue.Queue()
        self.running = True
        
    def add_task(self, task_func, *args, **kwargs):
        """添加任务到队列"""
        task = {
            'func': task_func,
            'args': args,
            'kwargs': kwargs,
            'id': id(task_func)
        }
        self.task_queue.put(task)
        
    def stop(self):
        """停止工作线程"""
        self.running = False
        self.task_queue.put(None)  # 添加停止信号
        
    def run(self):
        """线程主循环"""
        while self.running:
            try:
                task = self.task_queue.get(timeout=1)
                if task is None:  # 停止信号
                    break
                    
                # 执行任务
                try:
                    result = task['func'](*task['args'], **task['kwargs'])
                    self.task_completed.emit(result)
                except Exception as e:
                    self.task_error.emit(str(e))
                    
                self.task_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                self.task_error.emit(f"任务执行出错: {str(e)}")


class TaskManager(QObject):
    """任务管理器"""
    
    def __init__(self):
        super().__init__()
        self.worker = TaskWorker()
        self.worker.task_completed.connect(self._on_task_completed)
        self.worker.task_error.connect(self._on_task_error)
        self.worker.start()
        
        # 任务回调映射
        self.task_callbacks = {}
        
    def execute_async(self, task_func, callback=None, error_callback=None, *args, **kwargs):
        """异步执行任务"""
        task_id = id(task_func)
        
        if callback or error_callback:
            self.task_callbacks[task_id] = {
                'success': callback,
                'error': error_callback
            }
            
        self.worker.add_task(task_func, *args, **kwargs)
        
    def _on_task_completed(self, result):
        """任务完成处理"""
        # 这里可以根据需要处理结果
        pass
        
    def _on_task_error(self, error_msg):
        """任务错误处理"""
        # 这里可以根据需要处理错误
        pass
        
    def shutdown(self):
        """关闭任务管理器"""
        self.worker.stop()
        self.worker.wait()


class UIOptimizer(QObject):
    """UI优化器"""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_ui)
        self.update_timer.start(100)  # 每100ms更新一次UI
        
        # 缓存的更新数据
        self._pending_updates = {
            'progress': None,
            'speed': None,
            'eta': None,
            'status': None
        }
        
    def queue_progress_update(self, progress):
        """队列进度更新"""
        self._pending_updates['progress'] = progress
        
    def queue_speed_update(self, speed):
        """队列速度更新"""
        self._pending_updates['speed'] = speed
        
    def queue_eta_update(self, eta):
        """队列ETA更新"""
        self._pending_updates['eta'] = eta
        
    def queue_status_update(self, status):
        """队列状态更新"""
        self._pending_updates['status'] = status
        
    def _update_ui(self):
        """批量更新UI"""
        try:
            # 更新进度
            if self._pending_updates['progress'] is not None:
                if hasattr(self.main_window, 'progress_widget'):
                    self.main_window.progress_widget.update_progress(
                        self._pending_updates['progress']
                    )
                self._pending_updates['progress'] = None
                
            # 更新速度
            if self._pending_updates['speed'] is not None:
                if hasattr(self.main_window, 'progress_widget'):
                    self.main_window.progress_widget.update_speed(
                        self._pending_updates['speed']
                    )
                self._pending_updates['speed'] = None
                
            # 更新ETA
            if self._pending_updates['eta'] is not None:
                if hasattr(self.main_window, 'progress_widget'):
                    self.main_window.progress_widget.update_eta(
                        self._pending_updates['eta']
                    )
                self._pending_updates['eta'] = None
                
            # 更新状态
            if self._pending_updates['status'] is not None:
                if hasattr(self.main_window, 'status_indicator'):
                    self.main_window.status_indicator.set_custom(
                        self._pending_updates['status']
                    )
                self._pending_updates['status'] = None
                
        except Exception as e:
            # 忽略UI更新错误，避免影响主要功能
            pass


class PerformanceMonitor(QObject):
    """性能监控器"""
    
    def __init__(self):
        super().__init__()
        self.start_time = None
        self.download_start_time = None
        self.bytes_downloaded = 0
        self.total_bytes = 0
        
        # 性能统计
        self.stats = {
            'total_time': 0,
            'download_time': 0,
            'average_speed': 0,
            'peak_speed': 0,
            'files_downloaded': 0,
            'total_size': 0
        }
        
    def start_session(self):
        """开始会话"""
        self.start_time = time.time()
        self.reset_download_stats()
        
    def start_download(self):
        """开始下载"""
        self.download_start_time = time.time()
        
    def update_download_progress(self, bytes_downloaded, total_bytes=None):
        """更新下载进度"""
        self.bytes_downloaded = bytes_downloaded
        if total_bytes:
            self.total_bytes = total_bytes
            
    def finish_download(self):
        """完成下载"""
        if self.download_start_time:
            download_time = time.time() - self.download_start_time
            self.stats['download_time'] += download_time
            self.stats['files_downloaded'] += 1
            self.stats['total_size'] += self.bytes_downloaded
            
            # 计算平均速度
            if download_time > 0:
                speed = self.bytes_downloaded / download_time
                if speed > self.stats['peak_speed']:
                    self.stats['peak_speed'] = speed
                    
        self.reset_download_stats()
        
    def finish_session(self):
        """结束会话"""
        if self.start_time:
            self.stats['total_time'] = time.time() - self.start_time
            
            # 计算总体平均速度
            if self.stats['total_time'] > 0:
                self.stats['average_speed'] = self.stats['total_size'] / self.stats['total_time']
                
    def reset_download_stats(self):
        """重置下载统计"""
        self.download_start_time = None
        self.bytes_downloaded = 0
        self.total_bytes = 0
        
    def get_stats(self):
        """获取统计信息"""
        return self.stats.copy()
        
    def format_stats(self):
        """格式化统计信息"""
        stats = self.get_stats()
        
        def format_size(bytes_val):
            for unit in ['B', 'KB', 'MB', 'GB']:
                if bytes_val < 1024:
                    return f"{bytes_val:.1f} {unit}"
                bytes_val /= 1024
            return f"{bytes_val:.1f} TB"
            
        def format_speed(bytes_per_sec):
            return f"{format_size(bytes_per_sec)}/s"
            
        def format_time(seconds):
            if seconds < 60:
                return f"{seconds:.1f}秒"
            elif seconds < 3600:
                return f"{seconds/60:.1f}分钟"
            else:
                return f"{seconds/3600:.1f}小时"
                
        return {
            'total_time': format_time(stats['total_time']),
            'download_time': format_time(stats['download_time']),
            'average_speed': format_speed(stats['average_speed']),
            'peak_speed': format_speed(stats['peak_speed']),
            'files_downloaded': stats['files_downloaded'],
            'total_size': format_size(stats['total_size'])
        }


# 全局任务管理器实例
_task_manager = None

def get_task_manager():
    """获取全局任务管理器实例"""
    global _task_manager
    if _task_manager is None:
        _task_manager = TaskManager()
    return _task_manager

def shutdown_task_manager():
    """关闭全局任务管理器"""
    global _task_manager
    if _task_manager:
        _task_manager.shutdown()
        _task_manager = None
