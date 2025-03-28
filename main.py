"""
build by following -> https://www.jamesbowley.co.uk/qmd/opencv_cuda_python_windows.html#opencv-cuda-python-windows-cmake-flags

It is possible that OpenCV with CUDA has already precompiled binaries for windows. Check here -> https://github.com/cudawarped/opencv_contrib/releases
"""

import datetime
import shutil
import time
import requests
import os
import subprocess
import urllib.request

from utils import *

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
    print(" | downloading installer")

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
    cudnn_dir = r"C:\Program Files\NVIDIA\CUDNN"
    cuda_toolkit_dir = r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA"
    cudnn_newest_version = ""
    cuda_toolkit_newest_version = ""

    print("searching for cuDNN...")
    if not os.path.exists(cudnn_dir):
        print(f" | cuDNN not found, downloading cuDNN from source")

        os.makedirs("installers", exist_ok=True)
        installer_path = os.path.join("./installers", "cudnn_installer.exe")

        urllib.request.urlretrieve(install_link, installer_path)

        print(f" | running installer {installer_path}...")
        try:
            subprocess.run([installer_path, "/quiet"], check=True)
        except subprocess.CalledProcessError as e:
            print(f" | error during cuDNN installation: {e}")
            return
    else:
        print(" | found")

    if os.path.exists(cuda_toolkit_dir):
        cuda_toolkit_newest_version = os.path.join(cuda_toolkit_dir, sorted(os.listdir(cuda_toolkit_dir))[-1])

    if os.path.exists(cudnn_dir):
        cudnn_newest_version = os.path.join(cudnn_dir, sorted(os.listdir(cudnn_dir))[-1])

    # This code finds the newest cuDNN version and moves its 'bin', 'include', and 'lib' contents
    # into the corresponding directories of the latest CUDA Toolkit installation.  
    #  
    # It achieves this by listing the default installation locations of both libraries using `os.listdir()`,  
    # sorting them, and selecting the last element to determine the latest version.  
    # The files from the newest cuDNN version are then moved to the respective directories in the latest CUDA Toolkit.  
    move_contents(src=os.path.join(cudnn_newest_version, "bin", sorted(os.listdir(os.path.join(cudnn_newest_version, "bin")))[-1]), 
                  dst=os.path.join(cuda_toolkit_newest_version, "bin"))
    move_contents(src=os.path.join(cudnn_newest_version, "include", sorted(os.listdir(os.path.join(cudnn_newest_version, "include")))[-1]),
                  dst=os.path.join(cuda_toolkit_newest_version, "include", sorted(os.listdir(os.path.join(cuda_toolkit_newest_version, "include")))[0]))
    move_contents(src=os.path.join(cudnn_newest_version, "lib", sorted(os.listdir(os.path.join(cudnn_newest_version, "lib")))[-1]),
                  dst=os.path.join(cuda_toolkit_newest_version, "lib", sorted(os.listdir(os.path.join(cuda_toolkit_newest_version, "lib")))[0]))
    # move_contents(os.path.join(cudnn_newest_version, "x64"), os.path.join(cuda_toolkit_newest_version, "x64"))

    # C:\\Program Files\\NVIDIA\\CUDNN\\v9.8\\include\\v12.8
    # C:\Program Files\NVIDIA\CUDNN\v9.8\include\12.8

    cuda_paths = [
        r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.8\bin",
        r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.8\lib\x64",
        r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.8\include",
        r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.8\extras\CUPTI\lib64"
    ]

    add_to_system_path(cuda_paths)
    
    print(" | cuDNN installation and environment setup completed")


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
    print("building OpenCV...")

    os.makedirs("build", exist_ok=True)

    env = os.environ.copy()
    env["CMAKE_BUILD_PARALLEL_LEVEL"] = str(threads_number)

    cmake_command = [
        "cmake",
        "-S", "opencv",
        "-B", "build",
        "-G", "Visual Studio 17 2022",

        "-DOPENCV_EXTRA_MODULES_PATH=opencv_contrib/modules",

        "-DWITH_CUDA=ON",
        "-DOPENCV_DNN_CUDA=ON",
        "-DBUILD_opencv_dnn=ON",
        "-DENABLE_FAST_MATH=ON",
        "-DBUILD_opencv_world=ON",

        "-DBUILD_JAVA=OFF",
        "-DBUILD_opencv_java_bindings_generator=OFF",
        "-DBUILD_opencv_js=OFF",
        "-DBUILD_opencv_js_bindings_generator=OFF",
        "-DBUILD_opencv_objc_bindings_generator=OFF",
        "-DBUILD_opencv_python_bindings_generator=OFF",
        "-DBUILD_opencv_python_tests=OFF",
        "-DBUILD_opencv_ts=OFF",

        "-DCMAKE_CONFIGURATION_TYPES=Release",
        "-DCMAKE_BUILD_TYPE=Release"
    ]

    subprocess.run(cmake_command, check=True, env=env)

    cmake_build = [
        "cmake",
        "--build", "build",
        "--target", "INSTALL",
        "--config", "Release"
    ]
    subprocess.run(cmake_build, check=True, env=env)

    print(" | build complete")


def install_opencv():
    build_dir = os.path.abspath("build")

    install_command = [
        "cmake",
        "--build", build_dir,
        "--target", "INSTALL",
        "--config", "Release"
    ]

    subprocess.run(install_command, check=True)


if __name__ == "__main__":
    start_time = time.time()

    msvc_path = r"C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC"
    cl_version = sorted(os.listdir(msvc_path))[-1]
    cl_path = os.path.join(msvc_path, cl_version, r"bin\Hostx86\x86\cl.exe")

    check_program_exists(program_name="cl", 
                         program_path=cl_path,
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

    # If your system path is too long, CUDA will not add the path to its shared libraries C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\vxx.x\bin during installation. 
    # If you receive a warning about this at the end of the installation process do not forget to manually add the this to your system or user path.
    check_program_exists(program_name="nvcc", 
                         program_path=r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.8\bin\nvcc.exe",
                         install_link=r"https://developer.download.nvidia.com/compute/cuda/12.8.0/network_installers/cuda_12.8.0_windows_network.exe")
  
    install_cudnn(install_link=r"https://developer.download.nvidia.com/compute/cudnn/9.8.0/local_installers/cudnn_9.8.0_windows.exe")

    download_opencv()
    build_opencv()
    install_opencv()

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Setup finished in {str(datetime.timedelta(seconds=int(elapsed_time)))}")