#!/usr/bin/env python3
import redis
from collections import defaultdict
import re
import argparse
from typing import Dict, List, Tuple

class RedisKeySizeAnalyzer:
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0, password: str = None):
        """Initialize Redis connection."""
        self.redis_client = redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=True
        )

    def extract_pattern(self, key: str) -> str:
        """
        Extract pattern from key by replacing numbers with '#' and keeping structure.
        Example: 'user:123:profile' becomes 'user:#:profile'
        """
        return re.sub(r'\d+', '#', key)

    def get_key_size(self, key: str) -> int:
        """Get the memory usage of a key in bytes."""
        try:
            return self.redis_client.memory_usage(key) or 0
        except redis.exceptions.ResponseError:
            return 0

    def analyze_keys(self, match_pattern: str = '*') -> Dict[str, Dict]:
        """
        Analyze Redis keys and group them by pattern.
        Returns statistics for each pattern including total size, count, and average size.
        """
        pattern_stats = defaultdict(lambda: {'count': 0, 'total_size': 0, 'min_size': float('inf'), 'max_size': 0})
        
        # Scan all keys matching the pattern
        cursor = '0'
        while cursor != 0:
            cursor, keys = self.redis_client.scan(cursor=cursor, match=match_pattern, count=1000)
            cursor = int(cursor)
            
            for key in keys:
                pattern = self.extract_pattern(key)
                size = self.get_key_size(key)
                
                stats = pattern_stats[pattern]
                stats['count'] += 1
                stats['total_size'] += size
                stats['min_size'] = min(stats['min_size'], size)
                stats['max_size'] = max(stats['max_size'], size)
                
        # Calculate averages and format sizes
        for stats in pattern_stats.values():
            if stats['count'] > 0:
                stats['avg_size'] = stats['total_size'] / stats['count']
            if stats['min_size'] == float('inf'):
                stats['min_size'] = 0

        return pattern_stats

    def format_size(self, size_in_bytes: float) -> str:
        """Format size in bytes to human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_in_bytes < 1024:
                return f"{size_in_bytes:.2f} {unit}"
            size_in_bytes /= 1024
        return f"{size_in_bytes:.2f} TB"

    def print_analysis(self, pattern_stats: Dict[str, Dict]) -> None:
        """Print analysis results in a formatted table."""
        # Sort patterns by total size
        sorted_patterns = sorted(
            pattern_stats.items(),
            key=lambda x: x[1]['total_size'],
            reverse=True
        )

        # Print header
        print("\nRedis Key Pattern Analysis")
        print("-" * 100)
        print(f"{'Pattern':<40} {'Count':<10} {'Total Size':<15} {'Avg Size':<15} {'Min Size':<15} {'Max Size':<15}")
        print("-" * 100)

        # Print each pattern's statistics
        for pattern, stats in sorted_patterns:
            print(
                f"{pattern:<40} "
                f"{stats['count']:<10} "
                f"{self.format_size(stats['total_size']):<15} "
                f"{self.format_size(stats['avg_size']):<15} "
                f"{self.format_size(stats['min_size']):<15} "
                f"{self.format_size(stats['max_size']):<15}"
            )

def main():
    parser = argparse.ArgumentParser(description='Analyze Redis key sizes by pattern')
    parser.add_argument('--host', default='localhost', help='Redis host')
    parser.add_argument('--port', type=int, default=6379, help='Redis port')
    parser.add_argument('--db', type=int, default=0, help='Redis database number')
    parser.add_argument('--password', help='Redis password')
    parser.add_argument('--pattern', default='*', help='Key pattern to match (e.g., "user:*")')
    
    args = parser.parse_args()
    
    try:
        analyzer = RedisKeySizeAnalyzer(
            host=args.host,
            port=args.port,
            db=args.db,
            password=args.password
        )
        
        print(f"\nConnecting to Redis at {args.host}:{args.port}/db{args.db}")
        pattern_stats = analyzer.analyze_keys(args.pattern)
        analyzer.print_analysis(pattern_stats)
        
    except redis.exceptions.ConnectionError as e:
        print(f"Error connecting to Redis: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

"""
pthon analyze.py --host 127.0.0.1 --port 6380 --db 0 --password ""
"""