"""
Log Rotation Module
Manages log files and deletes logs older than specified days
"""
import os
import glob
from pathlib import Path
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class LogRotator:
    """Handles log rotation and cleanup"""
    
    def __init__(self, log_file, retention_days=7):
        """
        Initialize log rotator
        
        Args:
            log_file: Main log file path
            retention_days: Number of days to keep logs (default: 7)
        """
        self.log_file = Path(log_file)
        self.log_dir = self.log_file.parent
        self.log_name = self.log_file.stem
        self.log_ext = self.log_file.suffix
        self.retention_days = retention_days
    
    def rotate_log(self):
        """Rotate the current log file with timestamp"""
        if not self.log_file.exists():
            return
        
        # Get file size
        file_size = self.log_file.stat().st_size
        
        # Only rotate if file has content
        if file_size == 0:
            return
        
        # Create timestamped backup
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"{self.log_name}_{timestamp}{self.log_ext}"
        backup_path = self.log_dir / backup_name
        
        try:
            # Copy to backup
            import shutil
            shutil.copy2(self.log_file, backup_path)
            
            # Clear original file
            with open(self.log_file, 'w') as f:
                f.write('')
            
            logger.info(f"Log rotated to: {backup_name}")
            
        except Exception as e:
            logger.error(f"Error rotating log: {e}")
    
    def cleanup_old_logs(self):
        """Delete log files older than retention period"""
        if not self.log_dir.exists():
            return
        
        # Calculate cutoff date
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        deleted_count = 0
        
        try:
            # Find all log files with timestamp pattern
            pattern = f"{self.log_name}_*{self.log_ext}"
            log_files = glob.glob(str(self.log_dir / pattern))
            
            for log_path in log_files:
                try:
                    # Get file modification time
                    file_stat = os.stat(log_path)
                    file_date = datetime.fromtimestamp(file_stat.st_mtime)
                    
                    # Delete if older than retention period
                    if file_date < cutoff_date:
                        os.remove(log_path)
                        deleted_count += 1
                        logger.info(f"Deleted old log: {Path(log_path).name}")
                        
                except Exception as e:
                    logger.error(f"Error processing {log_path}: {e}")
            
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old log file(s)")
            else:
                logger.debug("No old logs to clean up")
                
        except Exception as e:
            logger.error(f"Error during log cleanup: {e}")
    
    def get_log_stats(self):
        """Get statistics about log files"""
        try:
            pattern = f"{self.log_name}*{self.log_ext}"
            log_files = glob.glob(str(self.log_dir / pattern))
            
            total_size = sum(os.path.getsize(f) for f in log_files)
            total_size_mb = total_size / (1024 * 1024)
            
            return {
                'count': len(log_files),
                'total_size_mb': round(total_size_mb, 2)
            }
        except Exception:
            return {'count': 0, 'total_size_mb': 0}
