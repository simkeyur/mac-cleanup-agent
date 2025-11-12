"""
System Cache Cleanup Module
Cleans up various system and application caches to free disk space
"""
import os
import shutil
import subprocess
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class SystemCacheCleaner:
    """Cleans system and application caches"""
    
    def __init__(self, config):
        self.config = config
        self.dry_run = config['safety']['dry_run']
        self.enabled_cleanups = config.get('cache_cleanup', {}).get('enabled', [])
        
    def get_dir_size(self, path):
        """Calculate directory size in MB"""
        try:
            total = 0
            for entry in Path(path).rglob('*'):
                if entry.is_file():
                    total += entry.stat().st_size
            return round(total / (1024 * 1024), 2)
        except Exception:
            return 0
    
    def clean_homebrew_cache(self):
        """Clean Homebrew cache"""
        if 'homebrew' not in self.enabled_cleanups:
            return 0
        
        try:
            cache_path = Path.home() / "Library/Caches/Homebrew"
            if not cache_path.exists():
                logger.info("Homebrew cache not found, skipping")
                return 0
            
            size_before = self.get_dir_size(cache_path)
            
            if self.dry_run:
                logger.info(f"[DRY RUN] Would clean Homebrew cache (~{size_before} MB)")
                return size_before
            
            # Use brew cleanup command
            result = subprocess.run(
                ['brew', 'cleanup', '-s'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                size_after = self.get_dir_size(cache_path)
                freed = size_before - size_after
                logger.info(f"Cleaned Homebrew cache: freed {freed} MB")
                return freed
            else:
                logger.warning(f"Homebrew cleanup failed: {result.stderr}")
                return 0
                
        except Exception as e:
            logger.error(f"Error cleaning Homebrew cache: {e}")
            return 0
    
    def clean_vscode_cache(self):
        """Clean VS Code cache"""
        if 'vscode' not in self.enabled_cleanups:
            return 0
        
        try:
            cache_paths = [
                Path.home() / "Library/Caches/com.microsoft.VSCode.ShipIt",
                Path.home() / "Library/Caches/com.microsoft.VSCode",
            ]
            
            total_freed = 0
            
            for cache_path in cache_paths:
                if not cache_path.exists():
                    continue
                
                size_before = self.get_dir_size(cache_path)
                
                if self.dry_run:
                    logger.info(f"[DRY RUN] Would clean {cache_path.name} (~{size_before} MB)")
                    total_freed += size_before
                else:
                    shutil.rmtree(cache_path, ignore_errors=True)
                    logger.info(f"Cleaned {cache_path.name}: freed {size_before} MB")
                    total_freed += size_before
            
            return total_freed
            
        except Exception as e:
            logger.error(f"Error cleaning VS Code cache: {e}")
            return 0
    
    def clean_pip_cache(self):
        """Clean pip cache"""
        if 'pip' not in self.enabled_cleanups:
            return 0
        
        try:
            cache_path = Path.home() / "Library/Caches/pip"
            if not cache_path.exists():
                logger.info("Pip cache not found, skipping")
                return 0
            
            size_before = self.get_dir_size(cache_path)
            
            if self.dry_run:
                logger.info(f"[DRY RUN] Would clean pip cache (~{size_before} MB)")
                return size_before
            
            result = subprocess.run(
                ['pip3', 'cache', 'purge'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info(f"Cleaned pip cache: freed {size_before} MB")
                return size_before
            else:
                logger.warning(f"Pip cache cleanup failed: {result.stderr}")
                return 0
                
        except Exception as e:
            logger.error(f"Error cleaning pip cache: {e}")
            return 0
    
    def clean_npm_cache(self):
        """Clean npm cache"""
        if 'npm' not in self.enabled_cleanups:
            return 0
        
        try:
            # Check if npm is installed
            npm_check = subprocess.run(
                ['which', 'npm'],
                capture_output=True,
                text=True
            )
            
            if npm_check.returncode != 0:
                logger.info("npm not found, skipping")
                return 0
            
            cache_path = Path.home() / "Library/Caches/npm"
            if cache_path.exists():
                size_before = self.get_dir_size(cache_path)
            else:
                size_before = 0
            
            if self.dry_run:
                logger.info(f"[DRY RUN] Would clean npm cache (~{size_before} MB)")
                return size_before
            
            result = subprocess.run(
                ['npm', 'cache', 'clean', '--force'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info(f"Cleaned npm cache: freed {size_before} MB")
                return size_before
            else:
                logger.warning(f"npm cache cleanup failed: {result.stderr}")
                return 0
                
        except Exception as e:
            logger.error(f"Error cleaning npm cache: {e}")
            return 0
    
    def clean_user_caches(self):
        """Clean safe user cache directories"""
        if 'user_caches' not in self.enabled_cleanups:
            return 0
        
        # Safe caches to clean (won't affect app functionality)
        safe_caches = [
            "com.apple.python",
            "node-gyp",
        ]
        
        total_freed = 0
        cache_dir = Path.home() / "Library/Caches"
        
        for cache_name in safe_caches:
            cache_path = cache_dir / cache_name
            
            if not cache_path.exists():
                continue
            
            try:
                size_before = self.get_dir_size(cache_path)
                
                if self.dry_run:
                    logger.info(f"[DRY RUN] Would clean {cache_name} (~{size_before} MB)")
                    total_freed += size_before
                else:
                    shutil.rmtree(cache_path, ignore_errors=True)
                    logger.info(f"Cleaned {cache_name}: freed {size_before} MB")
                    total_freed += size_before
                    
            except Exception as e:
                logger.error(f"Error cleaning {cache_name}: {e}")
        
        return total_freed
    
    def clean_chrome_cache(self):
        """Clean Google Chrome cache"""
        if 'chrome' not in self.enabled_cleanups:
            return 0
        
        try:
            chrome_caches = [
                Path.home() / "Library/Caches/Google/Chrome",
                Path.home() / "Library/Application Support/Google/Chrome/Default/Cache",
                Path.home() / "Library/Application Support/Google/Chrome/Default/Code Cache",
            ]
            
            total_freed = 0
            
            for cache_path in chrome_caches:
                if not cache_path.exists():
                    continue
                
                size_before = self.get_dir_size(cache_path)
                
                if self.dry_run:
                    logger.info(f"[DRY RUN] Would clean Chrome {cache_path.name} (~{size_before} MB)")
                    total_freed += size_before
                else:
                    shutil.rmtree(cache_path, ignore_errors=True)
                    logger.info(f"Cleaned Chrome {cache_path.name}: freed {size_before} MB")
                    total_freed += size_before
            
            if total_freed > 0 and not self.dry_run:
                logger.warning("Note: Chrome may need to be restarted for best performance")
            
            return total_freed
            
        except Exception as e:
            logger.error(f"Error cleaning Chrome cache: {e}")
            return 0
    
    def clean_safari_cache(self):
        """Clean Safari cache"""
        if 'safari' not in self.enabled_cleanups:
            return 0
        
        try:
            safari_caches = [
                Path.home() / "Library/Caches/com.apple.Safari",
                Path.home() / "Library/Safari/LocalStorage",
                Path.home() / "Library/Safari/Databases",
            ]
            
            total_freed = 0
            
            for cache_path in safari_caches:
                if not cache_path.exists():
                    continue
                
                size_before = self.get_dir_size(cache_path)
                
                if self.dry_run:
                    logger.info(f"[DRY RUN] Would clean Safari {cache_path.name} (~{size_before} MB)")
                    total_freed += size_before
                else:
                    if cache_path.is_dir():
                        shutil.rmtree(cache_path, ignore_errors=True)
                        cache_path.mkdir(exist_ok=True)  # Recreate empty dir
                    logger.info(f"Cleaned Safari {cache_path.name}: freed {size_before} MB")
                    total_freed += size_before
            
            if total_freed > 0 and not self.dry_run:
                logger.warning("Note: Safari may need to be restarted")
            
            return total_freed
            
        except Exception as e:
            logger.error(f"Error cleaning Safari cache: {e}")
            return 0
    
    def clean_firefox_cache(self):
        """Clean Firefox cache"""
        if 'firefox' not in self.enabled_cleanups:
            return 0
        
        try:
            firefox_profile_dir = Path.home() / "Library/Application Support/Firefox/Profiles"
            
            if not firefox_profile_dir.exists():
                logger.info("Firefox not found, skipping")
                return 0
            
            total_freed = 0
            
            # Find all profiles and clean their caches
            for profile in firefox_profile_dir.iterdir():
                if not profile.is_dir():
                    continue
                
                cache_path = profile / "cache2"
                if cache_path.exists():
                    size_before = self.get_dir_size(cache_path)
                    
                    if self.dry_run:
                        logger.info(f"[DRY RUN] Would clean Firefox cache (~{size_before} MB)")
                        total_freed += size_before
                    else:
                        shutil.rmtree(cache_path, ignore_errors=True)
                        logger.info(f"Cleaned Firefox cache: freed {size_before} MB")
                        total_freed += size_before
            
            if total_freed > 0 and not self.dry_run:
                logger.warning("Note: Firefox may need to be restarted")
            
            return total_freed
            
        except Exception as e:
            logger.error(f"Error cleaning Firefox cache: {e}")
            return 0
    
    def clean_all(self):
        """Run all enabled cache cleanups"""
        if not self.enabled_cleanups:
            logger.info("Cache cleanup disabled in config")
            return 0
        
        logger.info("=" * 60)
        logger.info("Starting Cache Cleanup")
        logger.info("=" * 60)
        
        total_freed = 0
        
        # Run each cleanup
        cleanups = [
            ("Homebrew", self.clean_homebrew_cache),
            ("VS Code", self.clean_vscode_cache),
            ("pip", self.clean_pip_cache),
            ("npm", self.clean_npm_cache),
            ("Chrome", self.clean_chrome_cache),
            ("Safari", self.clean_safari_cache),
            ("Firefox", self.clean_firefox_cache),
            ("User Caches", self.clean_user_caches),
        ]
        
        for name, cleanup_func in cleanups:
            try:
                freed = cleanup_func()
                total_freed += freed
            except Exception as e:
                logger.error(f"Error in {name} cleanup: {e}")
        
        logger.info("=" * 60)
        if self.dry_run:
            logger.info(f"Cache Cleanup Complete (DRY RUN): Would free ~{total_freed:.2f} MB")
        else:
            logger.info(f"Cache Cleanup Complete: Freed {total_freed:.2f} MB")
        logger.info("=" * 60)
        
        return total_freed
