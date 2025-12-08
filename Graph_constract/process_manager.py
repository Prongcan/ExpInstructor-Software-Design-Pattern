import json
import os
from datetime import datetime
from typing import List, Dict, Tuple


def save_progress(progress_file: str, processed_papers: List[str], failed_papers: List[str], 
                 results: List[Dict], current_index: int):
    """Persist progress to disk"""
    progress_data = {
        'processed_papers': processed_papers,
        'failed_papers': failed_papers,
        'results': results,
        'current_index': current_index,
        'timestamp': datetime.now().isoformat()
    }
    with open(progress_file, 'w', encoding='utf-8') as f:
        json.dump(progress_data, f, indent=2, ensure_ascii=False)

    
def load_progress(progress_file: str) -> Tuple[List[str], List[str], List[Dict], int]:
    """Load saved progress"""
    if os.path.exists(progress_file):
        with open(progress_file, 'r', encoding='utf-8') as f:
            progress_data = json.load(f)
        return (progress_data.get('processed_papers', []),
                progress_data.get('failed_papers', []),
                progress_data.get('results', []),
                progress_data.get('current_index', 0))
    return [], [], [], 0