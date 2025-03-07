# OpenCV on Cuda
Because C++ and its ecosystem, if they can be called that, are obsolete and overly complex for a user who is just trying to get into it, the setup process is long and highly error-prone. This script is designed to set up a CUDA & OpenCV starter project from which 
others can build, with no requirements other than Python 3, which can be installed from the Microsoft Store or the official [website](https://www.python.org/).


## Requirements
* **Python3 interpreter**


## Targets
For everything to work, the script will attempt to install several dependencies while always prompting for confirmation at each step in a comprehensive, verbose mode:

* **Git** – Required to download OpenCV from the official GitHub repository.
* **C++ Compiler** – In this case, MSVC.
* **CMake** – Used for generating build files and compiling the project.
* **CUDA Toolkit** – Provides the essential tools, libraries, and drivers needed to develop GPU-accelerated applications using NVIDIA’s CUDA architecture. It includes the NVCC compiler, CUDA libraries, and debugging tools.
* **cuDNN** – NVIDIA's GPU-accelerated deep learning library, optimized for high-performance neural network operations. It provides primitives for deep learning frameworks to efficiently run on CUDA-enabled GPUs, improving performance for training and inference tasks.


## Process
For each target or application, the script will first check if it is already installed to avoid unnecessary overhead and potential complications. The only exception is cuDNN, which must be installed and then added to the system environment variables.
Finally, the `include`, `lib` and `x64` files will be moved into the CUDA Toolkit directory.


## How to Use
First, clone this repository to your desired location:
```
git clone https://github.com/CL0001/opencv-auto-build.git
```
Alternatively, you can download it as a .zip file.

Once you have the script, download the necessary libraries. To keep everything organized and make cleanup easier, we will create a Python virtual environment and install all dependencies there.

Open a terminal in the directory where the script is located and run:
```
python -m venv env
```

This should only take a moment. Then, activate the newly created virtual environment with:
```
env/Scripts/activate
```

Next, install the required dependencies:
```
pip install -r requirements.txt
```

After this, everything should be set up and ready to run:
```
python main.py
```

Now, just follow the instructions in the terminal to proceed with the installation and setup.
