#!/usr/bin/env python
"""
Utility script to run the AWS Cloud configuration scan independently.
"""
import sys
import os
import json
import argparse

# Add app to path so we can run directly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.collectors.aws import AWSCollector

def main():
    parser = argparse.ArgumentParser(description="Run the CloudCompliance Sentinel AWS Resource Collector.")
    parser.add_argument("--demo", action="store_true", help="Force run in Mock Demo Mode.")
    parser.add_argument("--real", action="store_true", help="Force run in Real Cloud Mode (requires AWS credentials).")
    
    args = parser.parse_args()
    
    # Determine mode overrides
    demo_mode = None
    if args.demo:
        demo_mode = True
    elif args.real:
        demo_mode = False
        
    print("=" * 60)
    print("CloudCompliance Sentinel - AWS Scanner CLI")
    print("=" * 60)
    
    try:
        collector = AWSCollector(demo_mode=demo_mode)
        print(f"Status: Initialized (Demo Mode: {collector.demo_mode})")
        print("Action: Starting discovery scan...")
        
        resources = collector.collect_resources()
        
        print(f"Action: Scan complete. Discovered {len(resources)} resources.")
        print("-" * 60)
        
        # Serialize ResourceModels
        serialized_data = [res.model_dump() for res in resources]
        print(json.dumps(serialized_data, indent=2))
        
        print("-" * 60)
        print("Execution Success.")
        
    except Exception as e:
        print(f"Execution Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
