import os
import re
import argparse
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont
from svgpath2mpl import parse_path
import numpy as np
import xml.etree.ElementTree as ET
from convert_svg import convert_svg

def extract_svg_paths(svg_content):
    """从 SVG 内容中提取路径数据"""
    try:
        # 使用正则表达式提取路径数据
        path_pattern = r'd="([^"]*)"'
        paths = re.findall(path_pattern, svg_content)
        
        if paths:
            return paths[0]  # 返回第一个找到的路径
        
        # 如果没有找到路径，尝试解析 XML
        root = ET.fromstring(svg_content)
        ns = {'svg': 'http://www.w3.org/2000/svg'}
        path_elements = root.findall('.//svg:path', ns)
        
        if path_elements:
            return path_elements[0].get('d', '')
    
    except Exception as e:
        print(f"Error extracting SVG path: {e}")
    
    return ""

def svg_to_glyph(svg_path, char_code, em_size=1000):
    """将 SVG 路径转换为字形"""
    try:
        # 解析 SVG 路径
        path = parse_path(svg_path)
        
        # 创建字形笔
        pen = TTGlyphPen(None)
        
        # 获取路径顶点
        vertices = path.vertices
        codes = path.codes
        
        if len(vertices) == 0:
            raise ValueError("No vertices found in SVG path")
        
        # 计算SVG的边界框以便进行适当缩放
        x_coords = [v[0] for v in vertices]
        y_coords = [v[1] for v in vertices]
        if x_coords and y_coords:
            min_x, max_x = min(x_coords), max(x_coords)
            min_y, max_y = min(y_coords), max(y_coords)
            svg_width = max_x - min_x
            svg_height = max_y - min_y
            
            # 计算缩放因子，保持宽高比
            scale_factor = min(em_size * 0.8 / svg_width, em_size * 0.8 / svg_height) if svg_width > 0 and svg_height > 0 else 1.0
            
            # 添加 y 轴下沉偏移量
            y_sink_factor = 0.15 # 0 ~ 1.0, 0.15 为特别调制参数
            
            # 计算居中偏移
            x_offset = (em_size - svg_width * scale_factor) / 2 - min_x * scale_factor
            y_offset = (em_size - svg_height * scale_factor) / 2  + (em_size * y_sink_factor)
        else:
            scale_factor = 1.0
            x_offset = 0
            y_offset = 0
        
        # 根据 matplotlib 路径代码转换为 TTGlyphPen 命令
        i = 0
        while i < len(codes):
            code = int(codes[i]) if hasattr(codes[i], 'item') else codes[i]
            
            # MOVETO
            if code == 1:
                x = float(vertices[i][0]) * scale_factor + x_offset
                # 翻转Y坐标（TTF坐标系Y轴向上为正）
                y = em_size - (float(vertices[i][1]) * scale_factor + y_offset)
                pen.moveTo((x, y))
            # LINETO
            elif code == 2:
                x = float(vertices[i][0]) * scale_factor + x_offset
                y = em_size - (float(vertices[i][1]) * scale_factor + y_offset)
                pen.lineTo((x, y))
            # CURVE3 (quadratic Bézier)
            elif code == 3 and i+1 < len(vertices):
                x1 = float(vertices[i][0]) * scale_factor + x_offset
                y1 = em_size - (float(vertices[i][1]) * scale_factor + y_offset)
                x2 = float(vertices[i+1][0]) * scale_factor + x_offset
                y2 = em_size - (float(vertices[i+1][1]) * scale_factor + y_offset)
                pen.qCurveTo((x1, y1), (x2, y2))
                i += 1
            # CURVE4 (cubic Bézier)
            elif code == 4 and i+2 < len(vertices):
                x1 = float(vertices[i][0]) * scale_factor + x_offset
                y1 = em_size - (float(vertices[i][1]) * scale_factor + y_offset)
                x2 = float(vertices[i+1][0]) * scale_factor + x_offset
                y2 = em_size - (float(vertices[i+1][1]) * scale_factor + y_offset)
                x3 = float(vertices[i+2][0]) * scale_factor + x_offset
                y3 = em_size - (float(vertices[i+2][1]) * scale_factor + y_offset)
                pen.curveTo((x1, y1), (x2, y2), (x3, y3))
                i += 2
            # CLOSEPOLY
            elif code == 79:
                pen.closePath()
            
            i += 1
        
        # 确保路径关闭
        if len(codes) > 0:
            last_code = int(codes[-1]) if hasattr(codes[-1], 'item') else codes[-1]
            if last_code != 79:
                pen.closePath()
        
        return pen.glyph()
    
    except Exception as e:
        print(f"Error converting SVG to glyph for character code {char_code}: {e}")
        return None

def generate_font(svg_directory, output_font_path):
    base_name = os.path.splitext(os.path.basename(output_font_path))[0]
    
    # 创建字体构建器
    fb = FontBuilder(1000, isTTF=True, glyphDataFormat=1)
    
    # 设置字体信息
    fb.setupNameTable({
        "familyName": base_name,
        "styleName": "Regular",
        "uniqueFontIdentifier": f"{base_name}:Regular",
        "fullName": f"{base_name} Regular",
        "version": "Version 1.0",
        "psName": f"{base_name}-Regular",
        "manufacturer": "SVG Font Generator",
        "copyright": f"Copyright (c) {base_name} Font"
    })
    
    # 创建字形表
    glyphs = {}
    glyph_order = ['.notdef']  # 添加 .notdef 字形
    char_map = {}
    
    # 添加 .notdef 字形（空白字形）
    pen = TTGlyphPen(None)
    pen.moveTo((0, 0))
    pen.lineTo((0, 800))
    pen.lineTo((500, 800))
    pen.lineTo((500, 0))
    pen.closePath()
    glyphs['.notdef'] = pen.glyph()
    
    # 处理SVG文件
    processed_count = 0
    for svg_filename in sorted(os.listdir(svg_directory)):
        if svg_filename.endswith('.svg'):
            char = svg_filename.replace('.svg', '')
            char_code = ord(char) if len(char) == 1 else int(char) if char.isdigit() else None
            
            if char_code is None:
                print(f"Skipping {svg_filename}: Could not determine character code")
                continue
            
            # 读取SVG文件
            svg_path = os.path.join(svg_directory, svg_filename)
            
            try:
                with open(svg_path, 'r', encoding='utf-8') as f:
                    svg_content = f.read()
                
                # 修复 SVG 内容
                # fixed_svg = fix_svg_path(svg_content)
                fixed_svg = convert_svg(svg_content)
                
                # 提取 SVG 路径数据
                path_data = extract_svg_paths(fixed_svg)
                
                if not path_data:
                    print(f"Warning: No path data found in {svg_filename}")
                    continue
                
                # 转换为字形
                glyph = svg_to_glyph(path_data, char_code)
                
                if glyph:
                    # 使用字符或数字作为字形名称
                    glyph_name = f"uni{char_code:04X}" if char_code > 127 else char
                    
                    # 添加到字形表
                    glyphs[glyph_name] = glyph
                    glyph_order.append(glyph_name)
                    char_map[char_code] = glyph_name
                    processed_count += 1
                    print(f"Processed {svg_filename} as {glyph_name}")
            
            except Exception as e:
                print(f"Failed to process {svg_filename}: {e}")
    
    if processed_count == 0:
        print("Error: No valid glyphs were processed. Cannot generate font.")
        return False
    
    # 设置字形表和映射
    fb.setupGlyphOrder(glyph_order)
    fb.setupCharacterMap(char_map)
    fb.setupGlyf(glyphs)
    
    # 设置水平度量
    hmtx = {}
    for glyph_name in glyph_order:
        # 为每个字形设置宽度和左侧轴承
        if glyph_name == '.notdef':
            hmtx[glyph_name] = (500, 0)
        else:
            # 可以根据字形的实际宽度调整
            hmtx[glyph_name] = (800, 50)
    
    fb.setupHorizontalMetrics(hmtx)
    
    # 设置必要的表
    # fb.setupHorizontalHeader(ascent=800, descent=-200)
    # fb.setupOS2(sTypoAscender=800, sTypoDescender=-200, usWinAscent=800, usWinDescent=200)
    
    # 设置必要的表
    fb.setupHorizontalHeader(ascent=900, descent=-100)
    fb.setupOS2(sTypoAscender=900, sTypoDescender=-100, usWinAscent=900, usWinDescent=100)
    fb.setupPost()
    
    # 保存字体
    try:
        fb.save(output_font_path)
        print(f"Font successfully generated: {output_font_path}")
        return True
    except Exception as e:
        print(f"Error saving font: {e}")
        return False

def check_font(file_path):
    try:
        font = TTFont(file_path)
        
        # 打印基本信息
        print("\n--- Font Information ---")
        print("Font name:", font["name"].getDebugName(1))
        print("Family name:", font["name"].getDebugName(1))
        print("Full name:", font["name"].getDebugName(4))
        
        # 检查字形数量
        glyph_order = font.getGlyphOrder()
        glyph_count = len(glyph_order)
        print(f"Glyph count: {glyph_count}")
        
        # 检查每个字形
        print("\n--- Glyphs ---")
        for glyph_name in glyph_order[:10]:  # 只显示前10个字形
            print(f"Glyph: {glyph_name}")
        
        if glyph_count > 10:
            print(f"... and {glyph_count - 10} more glyphs")
        
        print("\nFont validation complete")
        return True
    
    except Exception as e:
        print(f"Error checking font: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate font from SVG images.")
    parser.add_argument('svg_directory', type=str, help='Directory containing the SVG images')
    parser.add_argument('output_font_path', type=str, help='Output path for the generated font file')
    args = parser.parse_args()
    
    print(f'Generating font from {args.svg_directory} to {args.output_font_path}')
    
    if generate_font(args.svg_directory, args.output_font_path):
        check_font(args.output_font_path)
