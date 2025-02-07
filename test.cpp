#include <iostream>
#include <opencv2/opencv.hpp>

int main() {
    // Print OpenCV version
    std::cout << "OpenCV version: " << CV_VERSION << std::endl;

    cv::Mat image = cv::imread("image.jpg");
    if (image.empty()) {
        std::cerr << "Error: Could not load image!" << std::endl;
        return -1;
    }

    // Display the image
    cv::imshow("Test Image", image);
    cv::waitKey(0); // Wait for a key press

    return 0;
}