import cv2
import easyocr
import numpy as np
import matplotlib.pyplot as plt

image_path = "sample.jpg"
img = cv2.imread(image_path)
python 
# Convert BGR → RGB (OpenCV loads in BGR)
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

plt.imshow(img_rgb)
plt.title("Original Image")
plt.axis("off")