import subprocess

def verify_cuda_acceleration() -> None:
    command = [
        r"build\bin\Debug\opencv_test_cudaarithmd.exe",
        "--gtest_filter=CUDA_Arithm/GEMM.Accuracy/0"
    ]
    subprocess.run(command, check=True)

verify_cuda_acceleration()