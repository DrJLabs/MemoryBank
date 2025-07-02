#!/usr/bin/env python
"""
Mem0 Reset CLI - Advanced reset functionality for memory system

This CLI provides fine-grained control over what gets reset in the memory system.
"""

import argparse
import sys
import logging
from mem0 import Memory
from mem0.memory.reset_manager import ResetOptions

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def confirm_reset(options: ResetOptions, summary: dict) -> bool:
    """Prompt user for confirmation before reset"""
    separator = "=" * 60
    logger.info("\n%s", separator)
    logger.info("RESET CONFIRMATION")
    logger.info(separator)
    logger.info("\nScope: %s", options.scope.value)
    logger.info("\nComponents to reset:")
    for component in summary["components_to_reset"]:
        logger.info("  - %s", component)
    
    logger.info("\nEstimated deletions:")
    for key, value in summary["estimated_deletions"].items():
        logger.info("  - %s: %s", key, value)
    
    logger.info("\n%s", separator)
    
    response = input("\nAre you sure you want to proceed? This action CANNOT be undone! (yes/no): ")
    return response.lower() == "yes"


def main():
    parser = argparse.ArgumentParser(
        description="Reset Mem0 memory system with fine-grained control",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full reset (deletes everything)
  python -m mem0.cli.reset
  
  # Keep graph data, reset vector and history
  python -m mem0.cli.reset --keep-graph
  
  # Keep vector data, reset graph and history  
  python -m mem0.cli.reset --keep-vector
  
  # Reset only the graph store
  python -m mem0.cli.reset --keep-vector --keep-history
  
  # Dry run to see what would be deleted
  python -m mem0.cli.reset --dry-run
  
  # Force reset without confirmation
  python -m mem0.cli.reset --force
  
  # Preserve specific user's data
  python -m mem0.cli.reset --preserve-user alice
        """
    )
    
    # Store selection arguments
    parser.add_argument(
        "--keep-vector",
        action="store_true",
        help="Keep vector store data (do not reset)"
    )
    parser.add_argument(
        "--keep-graph", 
        action="store_true",
        help="Keep graph store data (do not reset)"
    )
    parser.add_argument(
        "--keep-history",
        action="store_true", 
        help="Keep history database (do not reset)"
    )
    
    # Operation arguments
    parser.add_argument(
        "--force",
        action="store_true",
        help="Skip confirmation prompt"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deleted without actually deleting"
    )
    
    # Preservation arguments
    parser.add_argument(
        "--preserve-user",
        type=str,
        help="Preserve memories for specific user ID"
    )
    parser.add_argument(
        "--preserve-agent",
        type=str,
        help="Preserve memories for specific agent ID"
    )
    
    # Config file
    parser.add_argument(
        "--config",
        type=str,
        help="Path to Mem0 configuration file"
    )
    
    args = parser.parse_args()
    
    # Build preserve filters
    preserve_filters = {}
    if args.preserve_user:
        preserve_filters["user_id"] = args.preserve_user
    if args.preserve_agent:
        preserve_filters["agent_id"] = args.preserve_agent
        
    # Create reset options
    options = ResetOptions.from_cli_args(
        keep_vector=args.keep_vector,
        keep_graph=args.keep_graph,
        keep_history=args.keep_history,
        force=args.force,
        dry_run=args.dry_run,
        preserve_filters=preserve_filters if preserve_filters else None
    )
    
    try:
        # Initialize memory
        if args.config:
            import json
            with open(args.config, 'r') as f:
                config = json.load(f)
            memory = Memory.from_config(config)
        else:
            memory = Memory()
            
        # Get reset summary
        summary = memory.reset_manager.get_reset_summary(options)
        
        # Show summary for dry run
        if args.dry_run:
            separator = "=" * 60
            logger.info("\nDRY RUN MODE - No data will be deleted")
            logger.info("\n%s", separator)
            logger.info("RESET SUMMARY")
            logger.info(separator)
            logger.info("\nScope: %s", options.scope.value)
            logger.info("\nComponents that would be reset:")
            for component in summary["components_to_reset"]:
                logger.info("  - %s", component)
            logger.info("\nEstimated deletions:")
            for key, value in summary["estimated_deletions"].items():
                logger.info("  - %s: %s", key, value)
            if preserve_filters:
                logger.info("\nPreserve filters:")
                for key, value in preserve_filters.items():
                    logger.info("  - %s: %s", key, value)
            logger.info("\n%s", separator)
            return 0
            
        # Confirm if not forced
        if not args.force:
            if not confirm_reset(options, summary):
                logger.info("\nReset cancelled.")
                return 1
                
        # Execute reset
        logger.info("\nExecuting reset...")
        result = memory.reset(options)
        
        if result["success"]:
            logger.info("\n✅ Reset completed successfully!")
            logger.info("\nComponents reset:")
            for component in result["components_reset"]:
                logger.info("  - %s", component)
        else:
            logger.error("\n❌ Reset failed!")
            logger.error("\nErrors:")
            for error in result.get("errors", ["Unknown error"]):
                logger.error("  - %s", error)
            return 1
            
    except Exception as e:
        logger.error(f"Reset failed with error: {e}")
        return 1
        
    return 0


if __name__ == "__main__":
    sys.exit(main()) 