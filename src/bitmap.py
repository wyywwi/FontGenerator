import os
from PIL import Image

def bitmap_to_svg(bitmap_path, svg_path):
    # 首先转换图像格式为 BMP
    bmp_path = bitmap_path.replace('.png', '.bmp')
    if not os.path.exists(bmp_path):  # 如果 BMP 文件不存在，则创建它
        image = Image.open(bitmap_path)
        image.save(bmp_path)

    # 使用 potrace 的优化参数将 BMP 转换为 SVG
    os.system(f'.\\potrace\\bin\\potrace.exe {bmp_path} -s -o {svg_path} --opttolerance 0.2 --alphamax 1.0')
