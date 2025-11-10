"""
File Organizer Module
Handles file organization by year and type
"""
import os
import shutil
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class FileOrganizer:
    """Organizes files by year and type"""
    
    def __init__(self, config):
        self.config = config
        self.base_path = Path(config['organization']['base_path']).expanduser()
        self.misc_folder = config['organization']['misc_folder']
        self.file_types = config['file_types']
        self.dry_run = config['safety']['dry_run']
        self.min_age_days = config['safety']['min_age_days']
        self.exclude_patterns = config['safety']['exclude_patterns']
        
    def get_file_type(self, file_path):
        """Determine file type based on extension"""
        ext = file_path.suffix.lower()
        
        for category, extensions in self.file_types.items():
            if ext in extensions:
                return category
        
        return self.misc_folder
    
    def get_file_year(self, file_path):
        """Get the year when the file was created/modified"""
        try:
            # Try creation time first, fall back to modification time
            stat = file_path.stat()
            timestamp = getattr(stat, 'st_birthtime', stat.st_mtime)
            return datetime.fromtimestamp(timestamp).year
        except Exception as e:
            logger.warning(f"Could not get date for {file_path}: {e}")
            return datetime.now().year
    
    def should_skip_file(self, file_path):
        """Check if file should be skipped"""
        # Check exclude patterns
        for pattern in self.exclude_patterns:
            if pattern in str(file_path):
                return True
        
        # Check minimum age
        if self.min_age_days > 0:
            try:
                stat = file_path.stat()
                age_days = (datetime.now().timestamp() - stat.st_mtime) / 86400
                if age_days < self.min_age_days:
                    return True
            except Exception:
                pass
        
        return False
    
    def organize_file(self, file_path, file_type_override=None):
        """Organize a single file"""
        try:
            if not file_path.is_file():
                return False
            
            if self.should_skip_file(file_path):
                logger.debug(f"Skipping {file_path.name}")
                return False
            
            # Determine file type and year
            file_type = file_type_override or self.get_file_type(file_path)
            year = self.get_file_year(file_path)
            
            # Create destination path: base_path/year/type/filename
            dest_dir = self.base_path / str(year) / file_type
            dest_path = dest_dir / file_path.name
            
            # Handle duplicate filenames
            counter = 1
            original_dest = dest_path
            while dest_path.exists():
                stem = original_dest.stem
                suffix = original_dest.suffix
                dest_path = dest_dir / f"{stem}_{counter}{suffix}"
                counter += 1
            
            # Create directory and move file
            if self.dry_run:
                logger.info(f"[DRY RUN] Would move: {file_path} -> {dest_path}")
            else:
                dest_dir.mkdir(parents=True, exist_ok=True)
                shutil.move(str(file_path), str(dest_path))
                logger.info(f"Moved: {file_path.name} -> {year}/{file_type}/")
            
            return True
            
        except Exception as e:
            logger.error(f"Error organizing {file_path}: {e}")
            return False
    
    def organize_folder(self, folder_path, ollama_classifier=None):
        """Organize all files in a folder"""
        folder = Path(folder_path).expanduser()
        
        if not folder.exists():
            logger.warning(f"Folder does not exist: {folder}")
            return 0
        
        logger.info(f"Organizing folder: {folder}")
        organized_count = 0
        
        try:
            files = [f for f in folder.iterdir() if f.is_file()]
            
            for file_path in files:
                # Use Ollama for intelligent classification if available
                file_type = None
                if ollama_classifier and file_path.suffix.lower() not in [ext for exts in self.file_types.values() for ext in exts]:
                    file_type = ollama_classifier.classify_file(file_path)
                
                if self.organize_file(file_path, file_type):
                    organized_count += 1
            
            logger.info(f"Organized {organized_count} files from {folder}")
            
        except Exception as e:
            logger.error(f"Error organizing folder {folder}: {e}")
        
        return organized_count
    
    def organize_all(self, ollama_classifier=None):
        """Organize all configured folders"""
        total = 0
        folders = self.config['folders']
        
        logger.info(f"Starting organization of {len(folders)} folders")
        
        for folder in folders:
            count = self.organize_folder(folder, ollama_classifier)
            total += count
        
        logger.info(f"Total files organized: {total}")
        return total
