import subprocess
import os

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

install_opencv()