#!/usr/bin/env python
"""
Utility script to run both AWS and GCP configuration scans and print the combined results.
"""
import sys
import os
import json
import argparse

# Add app to path so we can run directly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.collectors.aws import AWSCollector
from app.collectors.gcp import GCPCollector

def main():
    parser = argparse.ArgumentParser(description="Run CloudCompliance Sentinel Multi-Cloud (AWS + GCP) Scanner.")
    parser.add_argument("--demo", action="store_true", help="Force run both in Demo Mode.")
    parser.add_argument("--real", action="store_true", help="Force run both in Real Mode (requires credentials).")
    
    args = parser.parse_args()
    
    demo_mode = None
    if args.demo:
        demo_mode = True
    elif args.real:
        demo_mode = False
        
    print("=" * 70)
    print("      CloudCompliance Sentinel - Multi-Cloud Discovery Scanner CLI")
    print("=" * 70)
    
    # 1. AWS Discovery
    print("\n[1/2] Initiating AWS Resource Scan...")
    try:
        aws_collector = AWSCollector(demo_mode=demo_mode)
        print(f"      Status: Initialized (Demo Mode: {aws_collector.demo_mode})")
        aws_resources = aws_collector.collect_resources()
        print(f"      Success: Discovered {len(aws_resources)} AWS resources.")
    except Exception as e:
        print(f"      Error scanning AWS: {e}", file=sys.stderr)
        aws_resources = []

    # 2. GCP Discovery
    print("\n[2/2] Initiating GCP Resource Scan...")
    try:
        gcp_collector = GCPCollector(demo_mode=demo_mode)
        print(f"      Status: Initialized (Demo Mode: {gcp_collector.demo_mode})")
        gcp_resources = gcp_collector.collect_resources()
        print(f"      Success: Discovered {len(gcp_resources)} GCP resources.")
    except Exception as e:
        print(f"      Error scanning GCP: {e}", file=sys.stderr)
        gcp_resources = []

    # Combine results
    combined_resources = aws_resources + gcp_resources
    
    print("\n" + "=" * 70)
    print(f"Summary: Scan complete. Total resources discovered: {len(combined_resources)}")
    print("=" * 70)
    
    # Serialize and print combined outputs
    serialized_data = [res.model_dump() for res in combined_resources]
    print(json.dumps(serialized_data, indent=2))
    
    print("\n" + "=" * 70)
    print("Execution Success.")

if __name__ == "__main__":
    main()
