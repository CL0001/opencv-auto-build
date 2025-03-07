# build by following -> https://www.jamesbowley.co.uk/qmd/opencv_cuda_python_windows.html#opencv-cuda-python-windows-cmake-flags

import shutil
import requests
import os
import subprocess

exec_commands = {}

def check_program_exists(program_name: str, program_path: str, install_link: str) -> None:
    print(f"searching for {program_name}...")
    if shutil.which(program_name) is not None == True:
        print(f" | found")
        exec_commands[program_name] = program_name
        return

    if os.path.exists(program_path):
        print(f" | found")
        exec_commands[program_name] = program_path
        return

    choice = input(f"{program_name} not found, do you want to (1)install, or (2)exit? ")
    if choice == "1":
        os.makedirs("installers", exist_ok=True)
        install_program(install_link)
        check_program_exists(program_name, program_path, install_link)
    else:
        exit(0)

def install_program(install_link: str) -> None:
    print(" | Downloading installer")

    output = os.path.join("./installers", install_link.split("/")[-1])
    request = requests.get(install_link)
    with open(output, "wb") as file:
        file.write(request.content)

    if output.endswith(".msi"):
        print(" | running installer")
        os.system(f"msiexec /i {output} /qn")
    else:
        print(" | running installer")
        os.startfile(output)

    input("press enter when installation is complete: ")

def install_cudnn(install_link: str) -> None:
    pass

def download_opencv() -> None:
    print("searching for opencv sources...")
    if not os.path.exists("./opencv"):
        print(" | opencv not found, installing opencv")
        os.system("git clone https://github.com/opencv/opencv.git")

    if not os.path.exists("./opencv_contrib"):
        print(" | opencv_contrib not found, installing opencv")
        os.system("git clone https://github.com/opencv/opencv_contrib.git")

    print(" | found")

def build_opencv(build_option: str = "vs", threads_number: int = 4) -> None:
    print("building opencv...")

    os.makedirs("build", exist_ok=True)

    subprocess.run(f"set CMAKE_BUILD_PARALLEL_LEVEL={threads_number}", shell=True, check=True)

    cmake_command = [
        "cmake",
        "-H" + "opencv",
        "-DOPENCV_EXTRA_MODULES_PATH=" + "opencv_contrib/modules",
        "-B" + "build",
        "-G" + "Visual Studio 17 2022",
        "-DINSTALL_TESTS=ON",
        "-DINSTALL_C_EXAMPLES=ON",
        "-DBUILD_EXAMPLES=ON",
        "-DBUILD_opencv_world=ON",
        "-DENABLE_CUDA_FIRST_CLASS_LANGUAGE=ON",
        "-DWITH_CUDA=ON",
        "-DCUDA_GENERATION=Auto",
        "-DBUILD_JAVA=OFF",
        "-DBUILD_opencv_java_bindings_generator=OFF",
        "-DBUILD_opencv_js=OFF",
        "-DBUILD_opencv_js_bindings_generator=OFF",
        "-DBUILD_opencv_objc_bindings_generator=OFF",
        "-DBUILD_opencv_python_bindings_generator=OFF",
        "-DBUILD_opencv_python_tests=OFF",
        "-DBUILD_opencv_ts=OFF"
    ]
    subprocess.run(cmake_command, check=True)

    cmake_build = [
        r"C:\Program Files\CMake\bin\cmake.exe",
        "--build", "build",
        "--target", "install",
        "--config", "Debug"
    ]
    subprocess.run(cmake_build, check=True)

    print(" | build complete")

# can be used only when build with python tests flag ON
def verify_build_cuda_acceleration() -> None:
    command = [
        r"build\bin\Debug\opencv_test_cudaarithmd.exe",
        "--gtest_filter=CUDA_Arithm/GEMM.Accuracy/0"
    ]
    subprocess.run(command, check=True)

def install_opencv():
    msbuild_path = r"C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe"
    install_vcxproj = os.path.abspath("build/INSTALL.vcxproj")

    install_command = [
        msbuild_path,
        install_vcxproj,
        "/p:Configuration=Release",
        "/p:Platform=x64",
        "/m"
    ]
    subprocess.run(install_command, check=True)

if __name__ == "__main__":
    check_program_exists(program_name="cl", 
                         program_path=r"C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.41.34120\bin\Hostx86\x86\cl.exe",
                         install_link=r"https://aka.ms/vs/17/release/vc_redist.x86.exe")

    check_program_exists(program_name="msbuild", 
                         program_path=r"C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe",
                         install_link=r"https://aka.ms/vs/17/release/VC_redist.x64.exe")

    check_program_exists(program_name="git", 
                         program_path=r"C:\Program Files\Git\cmd\git.exe",
                         install_link=r"https://github.com/git-for-windows/git/releases/download/v2.47.1.windows.2/Git-2.47.1.2-64-bit.exe")

    check_program_exists(program_name="cmake", 
                         program_path=r"C:\Program Files\CMake\bin\cmake.exe",
                         install_link=r"https://github.com/Kitware/CMake/releases/download/v3.31.5/cmake-3.31.5-windows-x86_64.msi")

    check_program_exists(program_name="nvcc", 
                         program_path=r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.6\bin\nvcc.exe",
                         install_link=r"https://developer.download.nvidia.com/compute/cuda/12.8.0/network_installers/cuda_12.8.0_windows_network.exe")

    # Install cuDNN, move lib, include, x-64 dirs content into cuda toolkit lib, include, x-64 dirs + add them into environment variables
    install_cudnn(install_link=r"https://developer.download.nvidia.com/compute/cudnn/9.7.1/local_installers/cudnn_9.7.1_windows.exe")

    download_opencv()

    build_opencv()

    # can be used only when build with python tests flag ON
    # verify_build_cuda_acceleration()

    install_opencv()