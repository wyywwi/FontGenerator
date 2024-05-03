import fontforge
import os

def generate_font(svg_directory, output_font_path):
    # 创建新字体对象
    font = fontforge.font()

    # 为所有SVG文件创建字符
    processed_chars = set()
    for svg_filename in os.listdir(svg_directory):
        if svg_filename.endswith('.svg'):
            char = svg_filename.replace('.svg', '')
            char_code = ord(char)
            processed_chars.add(char_code)
            glyph = font.createChar(char_code)
            glyph.importOutlines(os.path.join(svg_directory, svg_filename))
            glyph.width = 600

    # 字符回退，包括中文字符
    fallback_font = fontforge.open('/path/to/Times_New_Roman.ttf')  # 替换为 Times New Roman 路径
    fallback_font_chinese = fontforge.open('/path/to/Songti.ttf')   # 替换为 宋体 路径
    for i in range(32, 0x9FFF+1):
        if i not in processed_chars:
            if 0x4E00 <= i <= 0x9FFF:  # 中文字符范围
                font.selection.select(i)
                font.paste(fallback_font_chinese)
            else:
                font.selection.select(i)
                font.paste(fallback_font)

    # 生成字体文件
    font.generate(output_font_path)
