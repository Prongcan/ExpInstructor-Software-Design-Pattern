import logging
import sys
from datetime import datetime

def setup_logging(log_file: str = None) -> logging.Logger:
    """Configure logging"""
    if log_file is None:
        log_file = f"batch_graph_construction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)
