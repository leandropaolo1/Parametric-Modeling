import numpy as np
import time


def grad_descent_cpu(A, b, alpha=0.001, maxiter=1000, tol=1e-4):
    x = np.zeros_like(b)
    for i in range(maxiter):
        g = A @ x - b
        x -= alpha * g
        if np.linalg.norm(g) < tol:
            print(f"✅ CPU converged at iter {i}, ||g|| = {np.linalg.norm(g):.4e}")
            break
    return x


def main():
    n = 4096
    print(f"📐 Problem size: {n} variables")

    # Create a well-scaled symmetric positive-definite matrix
    A = np.random.randn(n, n).astype(np.float32)
    A = (A + A.T) / 2  # make symmetric
    A += n * np.eye(n, dtype=np.float32)  # make positive definite
    A /= np.linalg.norm(A)  # scale down

    b = np.random.rand(n).astype(np.float32)

    print("🔥 Warming up...")
    grad_descent_cpu(A, b, maxiter=10)

    print("⏱️ Benchmarking CPU gradient descent...")
    start = time.time()
    x = grad_descent_cpu(A, b, alpha=0.001, maxiter=500)
    end = time.time()

    print(f"💻 CPU time: {end - start:.6f} sec")


if __name__ == "__main__":
    main()
