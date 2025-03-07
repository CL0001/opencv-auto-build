"""
build by following -> https://www.jamesbowley.co.uk/qmd/opencv_cuda_python_windows.html#opencv-cuda-python-windows-cmake-flags

It is possible that OpenCV with CUDA has already precompiled binaries for windows. Check here -> https://github.com/cudawarped/opencv_contrib/releases
"""
import shutil
import requests
import os
import subprocess

import urllib.request

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
    os.makedirs("installers", exist_ok=True)
    installer_path = os.path.join("./installers", "cudnn_installer.exe")

    print(f"Downloading cuDNN from {install_link}...")
    urllib.request.urlretrieve(install_link, installer_path)

    print(f"Running installer {installer_path}...")
    try:
        subprocess.run([installer_path, "/quiet"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error during cuDNN installation: {e}")
        return
    
    cuda_dir = r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.0"
    
    cudnn_dir = os.path.join(cuda_dir, "v11.0")
    
    cudnn_lib_dir = os.path.join(cudnn_dir, "lib")
    cudnn_include_dir = os.path.join(cudnn_dir, "include")
    cudnn_x64_dir = os.path.join(cudnn_dir, "x64")

    if not os.path.exists(cudnn_lib_dir):
        os.makedirs(cudnn_lib_dir)
    if not os.path.exists(cudnn_include_dir):
        os.makedirs(cudnn_include_dir)
    if not os.path.exists(cudnn_x64_dir):
        os.makedirs(cudnn_x64_dir)

    cudnn_temp_dir = os.path.join("./installers", "cudnn_extracted")
    
    shutil.move(os.path.join(cudnn_temp_dir, "lib", "*"), cudnn_lib_dir)
    shutil.move(os.path.join(cudnn_temp_dir, "include", "*"), cudnn_include_dir)
    shutil.move(os.path.join(cudnn_temp_dir, "x64", "*"), cudnn_x64_dir)

    print("Updating system environment variables...")
    cudnn_lib_path = os.path.join(cudnn_lib_dir, "x64")
    
    os.environ["PATH"] += os.pathsep + cuda_dir + os.pathsep + cudnn_lib_path
    os.environ["CUDA_PATH"] = cuda_dir
    
    try:
        subprocess.run(f"setx PATH \"{os.environ['PATH']}\"", shell=True, check=True)
        subprocess.run(f"setx CUDA_PATH \"{cuda_dir}\"", shell=True, check=True)
        print("Environment variables updated successfully.")
    except Exception as e:
        print(f"Failed to update environment variables: {e}")
    
    print("cuDNN installation and environment setup completed!")


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
        "-B" + "build",
        "-G" + "Visual Studio 17 2022",

        "-DOPENCV_EXTRA_MODULES_PATH=" + "opencv_contrib/modules",

        "-DINSTALL_TESTS=ON",
        "-DINSTALL_C_EXAMPLES=ON",
        "-DBUILD_EXAMPLES=ON",

        "-DBUILD_opencv_world=ON",
        
        "-DENABLE_CUDA_FIRST_CLASS_LANGUAGE=ON",
        "-DWITH_CUDA=ON",
        "-DCUDA_GENERATION=Auto",
        "-DOPENCV_DNN_CUDA=ON",
        "-DBUILD_opencv_dnn=ON",
        "-DENABLE_FAST_MATH=ON",
        "-DCUDA_ARCH_BIN=Auto",

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
    """
    If your system path is too long, CUDA will not add the path to its shared libraries C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\vxx.x\bin during installation. 
    If you receive a warning about this at the end of the installation process do not forget to manually add the this to your system or user path.
    """
    check_program_exists(program_name="nvcc", 
                         program_path=r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.6\bin\nvcc.exe",
                         install_link=r"https://developer.download.nvidia.com/compute/cuda/12.8.0/network_installers/cuda_12.8.0_windows_network.exe")

    install_cudnn(install_link=r"https://developer.download.nvidia.com/compute/cudnn/9.7.1/local_installers/cudnn_9.7.1_windows.exe")

    download_opencv()

    build_opencv()

    # can be used only when build with python tests flag ON
    # verify_build_cuda_acceleration()

    install_opencv()