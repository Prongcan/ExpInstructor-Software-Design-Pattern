import os
import sys
# Ensure proper path setup
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Refactored with Template Method Pattern: Use the new evaluation flow
from Evaluation_utils.novelty_evaluation_flow import NoveltyEvaluationFlow
from Evaluation_utils.test_idea import raw_idea


def main() -> None:
    """
    Main function using Template Method Pattern.
    Refactored with Template Method Pattern.
    """
    # Refactored with Template Method Pattern: Simplified main logic using template method
    flow = NoveltyEvaluationFlow()
    result = flow.run(raw_idea)
    return result


if __name__ == "__main__":
    main()