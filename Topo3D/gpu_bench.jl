using AMDGPU, BenchmarkTools, Printf

function main()
    n = 2048
    println("📐 Matrix dimensions: $(n)x$(n)")

    gpu_available = false
    try
        dev = AMDGPU.device()
        arch = AMDGPU.HIP.gcn_arch(dev)
        println("🖥️  AMD GPU Device: ", dev)
        println("🧬 GPU Architecture: ", arch)
        gpu_available = true
    catch e
        println("❌ Failed to access/trust AMD GPU: ", e)
    end

    if gpu_available
        try
            println("📦 Allocating matrices on GPU...")
            A = ROCArray(rand(Float32, n, n))
            B = ROCArray(rand(Float32, n, n))

            println("🔥 Warming up GPU matmul...")
            C = A * B
            AMDGPU.synchronize()

            println("⏱️ Benchmarking GPU matmul...")
            suite = @benchmarkable begin
                C = $A * $B
                AMDGPU.synchronize()
            end evals = 1

            results = run(suite; samples=30)
            println("⚡ Median GPU time: ", @sprintf("%.6f", median(results.times) / 1e9), " sec")
        catch e
            println("❌ GPU matmul failed: ", e)
            println("⚠️ Likely due to missing support for your arch in rocBLAS (e.g., gfx1032).")
        end
    else
        println("⚠️ Falling back to CPU...")

        A = rand(Float32, n, n)
        B = rand(Float32, n, n)

        println("🔥 Warming up CPU matmul...")
        C = A * B

        println("⏱️ Benchmarking CPU matmul...")
        suite = @benchmarkable begin
            C = $A * $B
        end evals = 1

        results = run(suite; samples=30)
        println("💻 Median CPU time: ", @sprintf("%.6f", median(results.times) / 1e9), " sec")
    end
end

main()
