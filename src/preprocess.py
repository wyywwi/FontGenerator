from PIL import Image, ImageEnhance, ImageFilter
import cv2
import numpy as np

def preprocess_image(image_path, output_path):
    # 打开和转换图像为灰度
    img = Image.open(image_path).convert('L')
    # 增强对比度
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.0)
    # 锐化处理
    img = img.filter(ImageFilter.SHARPEN)
    # 自适应阈值二值化
    img_np = np.array(img)
    img_np = cv2.medianBlur(img_np, 5)
    img_np = cv2.adaptiveThreshold(img_np, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    img = Image.fromarray(img_np)
    img.save(output_path)
