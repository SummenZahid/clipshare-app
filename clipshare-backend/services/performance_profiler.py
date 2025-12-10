import time
import functools
from typing import Dict, List
from collections import defaultdict

performance_metrics = defaultdict(list)

def measure_time(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            performance_metrics[func.__name__].append(execution_time)
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            performance_metrics[func.__name__].append(execution_time)
            raise e
    return wrapper

def get_performance_stats() -> Dict:
    stats = {}
    for func_name, times in performance_metrics.items():
        if times:
            stats[func_name] = {
                'count': len(times),
                'avg_time': sum(times) / len(times),
                'min_time': min(times),
                'max_time': max(times),
                'total_time': sum(times)
            }
    return stats

def get_slow_endpoints(threshold: float = 1.0) -> List[Dict]:
    slow_endpoints = []
    for func_name, times in performance_metrics.items():
        avg_time = sum(times) / len(times) if times else 0
        if avg_time > threshold:
            slow_endpoints.append({
                'endpoint': func_name,
                'avg_time': avg_time,
                'count': len(times)
            })
    return sorted(slow_endpoints, key=lambda x: x['avg_time'], reverse=True)

def reset_metrics():
    performance_metrics.clear()

def optimize_query(query: str, params: Dict = None) -> str:
    if 'ORDER BY' in query.upper():
        query = query.replace('ORDER BY', 'ORDER BY c')
    return query

cache = {}

def cache_result(ttl: int = 300):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            if cache_key in cache:
                cached_time, cached_value = cache[cache_key]
                if time.time() - cached_time < ttl:
                    return cached_value
            result = func(*args, **kwargs)
            cache[cache_key] = (time.time(), result)
            return result
        return wrapper
    return decorator
