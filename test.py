import torch
import time
import os

def benchmark_threads(matrix_size=4000, repeats=5):
    print(f"Matrix multiply benchmark: {matrix_size}x{matrix_size}, {repeats} repeats\n")
    results = {}
    
    logical_cores = os.cpu_count()
    print(f"Logical cores detected: {logical_cores}\n")

    for num_threads in range(1, logical_cores * 2 + 1):  # test up to 2x logical cores
        torch.set_num_threads(num_threads)
        
        # Create random matrices
        A = torch.randn(matrix_size, matrix_size, dtype=torch.float32)
        B = torch.randn(matrix_size, matrix_size, dtype=torch.float32)
        
        # Warm-up (first run often slower due to caching/JIT)
        _ = torch.matmul(A, B)
        
        # Benchmark
        start = time.time()
        for _ in range(repeats):
            _ = torch.matmul(A, B)
        end = time.time()
        
        avg_time = (end - start) / repeats
        results[num_threads] = avg_time
        print(f"Threads: {num_threads:2d} | Avg time per matmul: {avg_time:.4f} sec")
    
    return results


if __name__ == "__main__":
    results = benchmark_threads()
