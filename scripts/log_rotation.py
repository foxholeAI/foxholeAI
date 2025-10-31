#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志轮转工具 - 定期轮转 ws.json 和其他日志文件
防止日志文件过大导致服务停止
"""

import os
import shutil
import gzip
from datetime import datetime
from pathlib import Path


class LogRotator:
    """日志轮转器"""
    
    def __init__(self, 
                 log_file: str,
                 max_size_mb: int = 50,
                 max_backups: int = 10,
                 compress: bool = True):
        """
        初始化日志轮转器
        
        Args:
            log_file: 日志文件路径
            max_size_mb: 最大文件大小（MB），超过此大小则轮转
            max_backups: 保留的备份文件数量
            compress: 是否压缩旧日志
        """
        self.log_file = Path(log_file)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.max_backups = max_backups
        self.compress = compress
        
    def should_rotate(self) -> bool:
        """检查是否需要轮转"""
        if not self.log_file.exists():
            return False
            
        file_size = self.log_file.stat().st_size
        return file_size >= self.max_size_bytes
    
    def rotate(self):
        """执行日志轮转"""
        if not self.log_file.exists():
            print(f"[LogRotator] 文件不存在: {self.log_file}")
            return
            
        try:
            # 生成备份文件名（带时间戳）
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{self.log_file.stem}_{timestamp}{self.log_file.suffix}"
            backup_path = self.log_file.parent / backup_name
            
            # 移动当前日志文件
            print(f"[LogRotator] 轮转日志: {self.log_file} -> {backup_path}")
            shutil.move(str(self.log_file), str(backup_path))
            
            # 压缩备份文件
            if self.compress:
                self._compress_file(backup_path)
            
            # 创建新的空日志文件
            self.log_file.touch()
            print(f"[LogRotator] 创建新日志文件: {self.log_file}")
            
            # 清理旧备份
            self._cleanup_old_backups()
            
            print(f"[LogRotator] 日志轮转完成")
            
        except Exception as e:
            print(f"[LogRotator] 日志轮转失败: {e}")
    
    def _compress_file(self, file_path: Path):
        """压缩文件"""
        try:
            gz_path = file_path.with_suffix(file_path.suffix + '.gz')
            print(f"[LogRotator] 压缩文件: {file_path} -> {gz_path}")
            
            with open(file_path, 'rb') as f_in:
                with gzip.open(gz_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # 删除原文件
            file_path.unlink()
            print(f"[LogRotator] 压缩完成，原文件已删除")
            
        except Exception as e:
            print(f"[LogRotator] 压缩失败: {e}")
    
    def _cleanup_old_backups(self):
        """清理旧备份文件"""
        try:
            # 查找所有备份文件
            pattern = f"{self.log_file.stem}_*"
            backups = sorted(
                self.log_file.parent.glob(pattern),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            
            # 删除超出数量的备份
            if len(backups) > self.max_backups:
                for backup in backups[self.max_backups:]:
                    print(f"[LogRotator] 删除旧备份: {backup}")
                    backup.unlink()
                    
        except Exception as e:
            print(f"[LogRotator] 清理旧备份失败: {e}")
    
    def check_and_rotate(self):
        """检查并轮转日志"""
        if self.should_rotate():
            file_size_mb = self.log_file.stat().st_size / 1024 / 1024
            print(f"[LogRotator] 日志文件过大 ({file_size_mb:.2f} MB)，开始轮转...")
            self.rotate()
        else:
            if self.log_file.exists():
                file_size_mb = self.log_file.stat().st_size / 1024 / 1024
                print(f"[LogRotator] 日志文件大小正常 ({file_size_mb:.2f} MB)")


def rotate_all_logs():
    """轮转所有日志文件"""
    print("=" * 70)
    print("日志轮转工具")
    print("=" * 70)
    print()
    
    # 定义需要轮转的日志文件
    log_configs = [
        {
            "file": "data/ws.json",
            "max_size_mb": 50,
            "max_backups": 10,
            "compress": True
        },
        {
            "file": "logs/ws_server.log",
            "max_size_mb": 100,
            "max_backups": 5,
            "compress": True
        },
        {
            "file": "logs/realtime_ca_detector.log",
            "max_size_mb": 100,
            "max_backups": 5,
            "compress": True
        }
    ]
    
    for config in log_configs:
        print(f"\n处理日志: {config['file']}")
        print("-" * 70)
        
        rotator = LogRotator(
            log_file=config["file"],
            max_size_mb=config["max_size_mb"],
            max_backups=config["max_backups"],
            compress=config["compress"]
        )
        
        rotator.check_and_rotate()
    
    print("\n" + "=" * 70)
    print("日志轮转完成")
    print("=" * 70)


if __name__ == "__main__":
    rotate_all_logs()


