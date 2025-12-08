import sys
import os
import json
import time
from typing import Dict, Optional

# Add parent directory to path to import LLM_service and core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.graph_facade import GraphConstructionFacade
from core.data_models import GraphConstructionInput, GraphConstructionResult
from Graph_constract.logger import setup_logging
from Graph_constract.process_manager import save_progress, load_progress

def transform_to_legacy_format(result: GraphConstructionResult) -> Optional[Dict]:
    """Transform facade result to legacy dictionary format."""
    if not result.success or not result.graph_data:
        return None
        
    legacy_edges = []
    for edge in result.graph_data.edges:
        legacy_edges.append({
            "source_name": edge.source,
            "target_name": edge.target,
            "relationship": edge.relation,
            "evidence": edge.description
        })
    
    return {
        'paper_id': result.input_data.paper_id,
        'review_id': result.input_data.review_id,
        'edges': legacy_edges,
        'edge_process_result': result.raw_response,
        'graph_data': result.graph_data.to_dict()
    }

def batch_process_iclr_data(input_file: str, output_dir: str, start_index: int = 0, 
                           max_papers: int = None, resume: bool = False) -> None:
    """Batch process ICLR paper data using GraphConstructionFacade"""
    logger = setup_logging()
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Progress file
    progress_file = os.path.join(output_dir, 'progress.json')
    
    # Load data
    logger.info(f"Loading data file: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        papers = json.load(f)
    
    total_papers = len(papers)
    if max_papers:
        total_papers = min(total_papers, max_papers)
    
    logger.info(f"Total papers to process: {total_papers}")
    
    # Reload progress when resuming
    processed_papers = []
    failed_papers = []
    results = []
    current_index = start_index
    
    if resume and os.path.exists(progress_file):
        processed_papers, failed_papers, results, current_index = load_progress(progress_file)
        logger.info(f"Resumed from checkpoint: processed {len(processed_papers)}, failed {len(failed_papers)}")
    
    # Initialize Facade
    facade = GraphConstructionFacade()
    
    # Batch settings
    batch_size = 100
    max_workers = 100  # Number of parallel threads
    
    # Build remaining paper list
    remaining_papers = []
    for i in range(current_index, total_papers):
        paper = papers[i]
        paper_id = paper['paper_id']
        
        if paper_id in processed_papers or paper_id in failed_papers:
            logger.info(f"Skipping paper already handled: {paper_id}")
            continue
        
        remaining_papers.append(paper)
    
    logger.info(f"{len(remaining_papers)} papers remaining; processing in batches of {batch_size}")
    
    # Iterate through batches
    for batch_start in range(0, len(remaining_papers), batch_size):
        batch_end = min(batch_start + batch_size, len(remaining_papers))
        batch = remaining_papers[batch_start:batch_end]
        
        logger.info(f"\n=== Starting batch {batch_start//batch_size + 1}: papers {batch_start+1}-{batch_end} (total remaining {len(remaining_papers)}) ===\n")
        
        # 1. Prepare inputs for the entire batch
        batch_inputs = []
        paper_map = {} # paper_id -> list of review_ids
        
        for paper in batch:
            paper_id = paper['paper_id']
            review_contents = paper.get('review_contents', [])
            
            if not review_contents:
                logger.warning(f"Paper {paper_id} has no review content")
                failed_papers.append(paper_id) # Mark as failed/skipped
                continue
                
            paper_map[paper_id] = []
            for review in review_contents:
                review_id = review['review_id']
                review_content = review['content']
                
                inp = GraphConstructionInput(
                    paper_id=paper_id,
                    review_id=review_id,
                    review_content=review_content
                )
                batch_inputs.append(inp)
                paper_map[paper_id].append(review_id)
        
        if not batch_inputs:
            logger.info("No valid reviews in this batch.")
            continue

        # 2. Execute batch using Facade
        logger.info(f"Submitting {len(batch_inputs)} reviews to facade...")
        batch_results = facade.batch_construct_graphs(batch_inputs, max_workers=max_workers)
        
        # 3. Process results
        # Group results by paper_id
        results_by_paper = {}
        for res in batch_results:
            pid = res.input_data.paper_id
            if pid not in results_by_paper:
                results_by_paper[pid] = []
            
            if res.success:
                legacy_res = transform_to_legacy_format(res)
                if legacy_res:
                    results_by_paper[pid].append(legacy_res)
            else:
                logger.error(f"Failed review {res.input_data.review_id} for paper {pid}: {res.error_message}")

        # 4. Save per-paper results and update status
        for paper in batch:
            paper_id = paper['paper_id']
            if paper_id in failed_papers: continue # Already marked as failed above
            
            paper_res_list = results_by_paper.get(paper_id, [])
            
            if paper_res_list:
                # Save results for this paper
                paper_output_file = os.path.join(output_dir, f"{paper_id}_graph.json")
                with open(paper_output_file, 'w', encoding='utf-8') as f:
                    json.dump(paper_res_list, f, indent=2, ensure_ascii=False)
                
                results.extend(paper_res_list)
                processed_papers.append(paper_id)
                logger.info(f"Paper {paper_id} finished with {len(paper_res_list)} reviews")
            else:
                # If we expected reviews but got none (all failed), mark paper as failed
                if paper_id in paper_map and paper_map[paper_id]:
                     failed_papers.append(paper_id)
                     logger.warning(f"All reviews failed for paper {paper_id}")
                # If it had no reviews to begin with, it was handled in step 1
        
        # Save checkpoint after each batch
        actual_progress = current_index + batch_end
        save_progress(progress_file, processed_papers, failed_papers, results, actual_progress)
        logger.info(f"Processed {batch_end}/{len(remaining_papers)} papers; progress saved")
        
        # Pause between batches
        time.sleep(2)
    
    # Save final merged results
    final_output_file = os.path.join(output_dir, 'all_graphs.json')

    if os.path.exists(final_output_file):
        with open(final_output_file, 'r', encoding='utf-8') as f:
            try:
                existing_results = json.load(f)
                if not isinstance(existing_results, list):
                    existing_results = [existing_results]
            except json.JSONDecodeError:
                existing_results = []
    else:
        existing_results = []

    if isinstance(results, list):
        existing_results.extend(results)
    else:
        existing_results.append(results)

    with open(final_output_file, 'w', encoding='utf-8') as f:
        json.dump(existing_results, f, indent=2, ensure_ascii=False)
    
    # Save summary stats
    stats = {
        'total_papers': total_papers,
        'processed_papers': len(processed_papers),
        'failed_papers': len(failed_papers),
        'total_reviews': len(results),
        'processed_paper_ids': processed_papers,
        'failed_paper_ids': failed_papers
    }
    
    stats_file = os.path.join(output_dir, 'processing_stats.json')
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    
    logger.info("Batch processing finished!")
    logger.info(f"Papers processed successfully: {len(processed_papers)}")
    logger.info(f"Papers failed: {len(failed_papers)}")
    logger.info(f"Total review graphs generated: {len(results)}")
    logger.info(f"Results stored in: {output_dir}")

def main():
    batch_process_iclr_data(
        input_file='data/ICLR/iclr2025_simple.json',
        output_dir='result_v2',
        start_index=9000,
        max_papers=9881,
        resume=False
    )

if __name__ == "__main__":
    main()
