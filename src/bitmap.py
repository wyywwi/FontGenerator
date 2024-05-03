import os

def bitmap_to_svg(bitmap_path, svg_path):
    # 使用potrace的优化参数
    os.system(f'../potrace/bin/potrace.exe {bitmap_path} -s -o {svg_path} --opttolerance 0.2 --alphamax 1.0 --curve-tightness 0.5')
