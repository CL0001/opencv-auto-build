import shutil
import requests
import os
from typing import List
import subprocess


def check_program_exists(name: str) -> bool:
    return shutil.which(name) is not None


def verify_program(program: str, names: List[str], possible_paths: List[str], install_link: str) -> str:
    for name in names:
        if check_program_exists(name):
            print(f"{program} ({name}) found")
            return name

    for possible_path in possible_paths:
        if os.path.exists(possible_path):
            print(f"{program} ({possible_path}) found")
            return possible_path

    choice = input(f"{program} not found, do you want to specify (1)path, (2)install, or (3)exit? ")
    if choice == "1":
        specific_path = input(f"| Enter path for {program}: ")
        if os.path.exists(specific_path):
            print(f"| {specific_path} valid")
        else:
            print(f"| {specific_path} invalid, exiting...")
            exit(1)
    elif choice == "2":
        print("| Downloading installer")
        filename = install_link.split("/")[-1]
        r = requests.get(install_link)
        with open(filename, "wb") as file:
            file.write(r.content)

        if filename.endswith(".msi"):
            os.system(f"msiexec /i {filename} /qn")
        else:
            os.startfile(filename)

        print(f"Restart this script when {program} is installed (you may need to restart your console as well)")
        exit(0)
    else:
        exit(0)


gpp = verify_program("cl", ["cl", "cl.exe"], [
    r"C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.41.34120\bin\Hostx86\x86\cl.exe"],
                     "https://aka.ms/vs/17/release/vc_redist.x86.exe")
cmake = verify_program("cmake", ["cmake"], [""],
                       "https://github.com/Kitware/CMake/releases/download/v3.31.5/cmake-3.31.5-windows-x86_64.msi")
git = verify_program("git", ["git"], [r"C:\Program Files\Git\cmd\git.exe"],
                     "https://github.com/git-for-windows/git/releases/download/v2.47.1.windows.2/Git-2.47.1.2-64-bit.exe")
msbuild = verify_program("msbuild", ["msbuild"],
                         [
                             r"C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\amd64\MSBuild.exe",
                             r"C:\Windows\Microsoft.NET\Framework\v4.0.30319\MSBuild.exe"],
                         "https://aka.ms/vs/17/release/VC_redist.x64.exe")

if not os.path.exists("opencv"):
    os.system("git clone https://github.com/opencv/opencv")
elif not os.path.isdir("opencv"):
    os.remove("opencv")
    os.system("git clone https://github.com/opencv/opencv")
else:
    print("opencv dir found")

# OpenCV build process
opencv_dir = "opencv"
build_dir = os.path.join(opencv_dir, "out")  # Create a build directory inside OpenCV

if not os.path.exists(opencv_dir):
    os.system("git clone https://github.com/opencv/opencv")
elif not os.path.isdir(opencv_dir):
    os.remove(opencv_dir)
    os.system("git clone https://github.com/opencv/opencv")
else:
    print("opencv dir found")

if not os.path.exists(build_dir):
    os.makedirs(build_dir)

os.chdir(build_dir)

cmake_command = [
    cmake,
    "-A", "x64",
    "-DCMAKE_BUILD_TYPE=Release",
    "-DBUILD_opencv_world=ON",
    # cuda
    "-DCUDA_NVCC_FLAGS=\"-gencode arch=compute_80,code=sm_80\"",
    "-DCUDA_ARCHITECTURES=80",
    ".."
]
subprocess.run(cmake_command, check=True)

msbuild_command = [
    msbuild,
    "opencv.sln",
    "/p:Configuration=Release"
]
subprocess.run(msbuild_command, check=True)

print("lib path:", os.path.join(build_dir, "lib"))
print("include path:", os.path.join(build_dir, "include"))

os.chdir("..")

# create 'out' dir in opencv then enter it and run following:
# cmake -A x64 -DCMAKE_BUILD_TYPE=Release -DBUILD_opencv_world=ON ..   | cmake -A x64 -DCMAKE_BUILD_TYPE=Release -DBUILD_opencv_world=ON -DCUDA_NVCC_FLAGS="-gencode arch=compute_80,code=sm_80" -DCUDA_ARCHITECTURES=80 ..
# msbuild opencv.sln /p:Configuration=Release  |  msbuild opencv.sln /p:Configuration=Release
# print 'lib' path and 'include' path
