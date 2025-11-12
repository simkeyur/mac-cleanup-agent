#!/usr/bin/env python3
"""
Mac Cleanup Agent
Organizes files in Downloads, Documents, and Desktop folders by year and type
Uses Ollama for intelligent file classification
"""
import os
import sys
import logging
import argparse
from pathlib import Path
import yaml

from file_organizer import FileOrganizer
from ollama_classifier import OllamaClassifier
from log_rotator import LogRotator
from cache_cleaner import SystemCacheCleaner


def load_config(config_path='config.yaml'):
    """Load configuration from YAML file"""
    try:
        # Try local config first
        local_config = Path('config.local.yaml')
        if local_config.exists():
            config_path = local_config
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        print(f"Error loading config: {e}")
        sys.exit(1)


def setup_logging(config):
    """Setup logging configuration"""
    log_level = config['logging']['level']
    log_file = config['logging']['file']
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level))
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level))
    console_format = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)
    
    return logger


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Mac Cleanup Agent - Organize your files intelligently'
    )
    parser.add_argument(
        '--config',
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without moving files'
    )
    parser.add_argument(
        '--no-ai',
        action='store_true',
        help='Disable Ollama AI classification'
    )
    parser.add_argument(
        '--folder',
        help='Organize specific folder instead of all configured folders'
    )
    parser.add_argument(
        '--skip-cache-cleanup',
        action='store_true',
        help='Skip system cache cleanup'
    )
    parser.add_argument(
        '--cache-only',
        action='store_true',
        help='Only run cache cleanup, skip file organization'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Override dry-run from command line
    if args.dry_run:
        config['safety']['dry_run'] = True
    
    # Setup logging
    logger = setup_logging(config)
    
    # Initialize log rotator and clean old logs
    retention_days = config['logging'].get('retention_days', 7)
    log_rotator = LogRotator(config['logging']['file'], retention_days)
    log_rotator.cleanup_old_logs()
    
    # Get log stats
    log_stats = log_rotator.get_log_stats()
    
    logger.info("=" * 60)
    logger.info("Mac Cleanup Agent Starting")
    logger.info("=" * 60)
    logger.debug(f"Log files: {log_stats['count']}, Total size: {log_stats['total_size_mb']} MB")
    
    if config['safety']['dry_run']:
        logger.warning("DRY RUN MODE - No files will be moved")
    
    # Run cache cleanup (unless skipped or in cache-only mode)
    if not args.skip_cache_cleanup or args.cache_only:
        cache_cleaner = SystemCacheCleaner(config)
        cache_cleaner.clean_all()
    
    # Skip file organization if cache-only mode
    if args.cache_only:
        logger.info("Cache-only mode - skipping file organization")
        sys.exit(0)
    
    # Initialize Ollama classifier
    ollama_classifier = None
    if not args.no_ai:
        ollama_classifier = OllamaClassifier(config)
        if ollama_classifier.is_available():
            logger.info(f"Ollama AI classification enabled (model: {config['ollama']['model']})")
        else:
            logger.warning("Ollama not available - using rule-based classification only")
            ollama_classifier = None
    else:
        logger.info("AI classification disabled")
    
    # Initialize file organizer
    organizer = FileOrganizer(config)
    
    # Organize files
    try:
        if args.folder:
            # Organize specific folder
            count = organizer.organize_folder(args.folder, ollama_classifier)
        else:
            # Organize all configured folders
            count = organizer.organize_all(ollama_classifier)
        
        logger.info("=" * 60)
        if config['safety']['dry_run']:
            logger.info(f"DRY RUN COMPLETE - Would organize {count} files")
        else:
            logger.info(f"CLEANUP COMPLETE - Organized {count} files")
        logger.info("=" * 60)
        
    except KeyboardInterrupt:
        logger.info("Cleanup interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
