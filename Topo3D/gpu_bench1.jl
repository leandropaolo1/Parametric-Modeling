using AMDGPU, BenchmarkTools, LinearAlgebra, Statistics, Plots

function grad_descent_gpu(A, b; α=0.001f0, maxiter=1000, tol=1e-4)
    x = ROCArray(zeros(Float32, size(b)))
    for i in 1:maxiter
        g = A * x .- b
        x = x .- α .* g  # Avoid .= to reduce kernel issues
        AMDGPU.synchronize()
        if norm(Array(g)) < tol
            break
        end
    end
    return Array(x)
end

function run_gpu_benchmarks()
    sizes = [512, 1024, 2048, 4096 * 2]
    gpu_times = Float64[]

    for n in sizes
        println("\n📐 Problem size: $n")

        A = Symmetric(rand(Float32, n, n)) + n * I
        b = rand(Float32, n)

        try
            A_gpu = ROCArray(A)
            b_gpu = ROCArray(b)

            println("🚀 Running GPU gradient descent...")
            # Warm-up
            grad_descent_gpu(A_gpu, b_gpu; maxiter=10)

            # Benchmark
            t_gpu = @belapsed grad_descent_gpu($A_gpu, $b_gpu; maxiter=500) evals = 1 samples = 10
            println("⚡ Median GPU time: ", round(t_gpu, digits=6), " sec")
            push!(gpu_times, t_gpu)
        catch e
            println("❌ GPU failed at size $n: $e")
            push!(gpu_times, NaN)
        end
    end

    return sizes, gpu_times
end

function plot_gpu_results(sizes, gpu_times)
    plot(
        sizes,
        gpu_times,
        label="GPU",
        lw=3,
        marker=:diamond,
        xlabel="Problem Size (n)",
        ylabel="Time (seconds)",
        yscale=:log10,
        title="GPU Gradient Descent Runtime",
        grid=true,
    )
end

# --- Run ---
sizes, gpu_times = run_gpu_benchmarks()
fig = plot_gpu_results(sizes, gpu_times)
display(fig)                 # Show if possible
savefig(fig, "gpu_plot.png") # Also save for safety
println("📊 Plot saved as gpu_plot.png")