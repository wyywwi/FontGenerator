import argparse
import fontforge
import os

def generate_font(svg_directory, output_font_path):
    # 创建新字体对象
    font = fontforge.font()
    font.fontname = "GeneratedFont-001"
    font.familyname = "GeneratedFont"
    font.fullname = "Generated Font 001"
    font.encoding = "UnicodeFull"

    # 为所有SVG文件创建字符
    processed_chars = set()
    for svg_filename in os.listdir(svg_directory):
        if svg_filename.endswith('.svg'):
            char = svg_filename.replace('.svg', '')
            char_code = ord(char)
            processed_chars.add(char_code)
            glyph = font.createChar(char_code)
            if not glyph.importOutlines(os.path.join(svg_directory, svg_filename)):
                print(f"Failed to import outlines for {char}")
            glyph.width = 600
            if glyph.layers[1].isEmpty():
                print(f"Glyph {char} is empty after attempting to import outlines.")


    # 字符回退，包括中文字符
    print(os.getcwd())
    fallback_font = fontforge.open('.\\fonts\\basic\\TimesNewRoman.ttf')  # Times New Roman 路径
    print("Times New Roman successfully imported")
    fallback_font_chinese = fontforge.open('.\\fonts\\basic\\STSong.ttf')   # 宋体 路径
    print("STSong successfully imported")

    for char in processed_chars:
        print(char)

    # 回退
    # 只处理在主字体编码范围内的字符
    for i in range(32, 0x9FFF + 1):
        if i not in processed_chars:
            if 0x4E00 <= i <= 0x9FFF:
                if i in fallback_font_chinese:
                    fallback_font_chinese.selection.select(('unicode',), i)
                    glyph = fallback_font_chinese.copy()
                    if i in font:
                        font.selection.select(('unicode',), i)
                        font.paste()
            else:
                if i in fallback_font:
                    fallback_font.selection.select(('unicode',), i)
                    glyph = fallback_font.copy()
                    if i in font:
                        font.selection.select(('unicode',), i)
                        font.paste()

    # for glyph in font.glyphs():
    #     glyph.correctDirection()

    if sum(1 for _ in font.glyphs()) == 0:
        raise Exception("No valid glyphs in font. Cannot generate TTF.")

    # 生成字体文件
    font.generate(output_font_path, "ttf")

def check_font(file_path):
    # 打开字体文件
    font = fontforge.open(file_path)

    # 打印基本信息
    print("Font name:", font.fontname)
    print("Family name:", font.familyname)
    print("Full name:", font.fullname)
    glyph_count = sum(1 for _ in font.glyphs())
    print("Glyph count:", glyph_count)

    # 检查每个字形的基本属性
    for glyph in font.glyphs():
        print("Glyph:", glyph.glyphname, "Unicode:", glyph.unicode)

    # 使用FontForge的验证功能
    problems = font.validate()
    if problems != 0:
        print("Validation found problems:", problems)
    else:
        print("No validation problems found.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate font from svg images.")
    parser.add_argument('svg_directory', type=str, help='Directory containing the svg images')
    parser.add_argument('output_font_path', type=str, help='Output path for the generated font file')
    args = parser.parse_args()
    # main(args.input_dir, args.output_font_path)
    print(f'Generate Font: ')
    generate_font(args.svg_directory, args.output_font_path)
    check_font(args.output_font_path)