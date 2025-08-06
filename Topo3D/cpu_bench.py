import numpy as np
from timeit import repeat

n = 2048  # Matrix size — same as Julia
A = np.random.rand(n, n).astype(np.float32)
B = np.random.rand(n, n).astype(np.float32)

# Warm-up
_ = A @ B

# Time it
times = repeat("A @ B", globals=globals(), number=1, repeat=30)
median = sorted(times)[len(times) // 2]


print(f"🧠 NumPy CPU median time for {n}x{n}: {median:.6f} seconds")
