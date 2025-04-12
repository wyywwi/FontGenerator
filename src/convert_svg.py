import xml.etree.ElementTree as ET
import re

def parse_path(d):
    """解析SVG路径数据"""
    tokens = re.findall(r'([A-Za-z])|(-?\d+\.?\d*)', d)
    tokens = [token[0] if token[0] else float(token[1]) for token in tokens]
    
    commands = []
    i = 0
    while i < len(tokens):
        if isinstance(tokens[i], str):  # 如果是命令
            cmd = tokens[i]
            i += 1
        # 根据命令收集参数
        if cmd == 'M' or cmd == 'm':  # 移动命令
            commands.append((cmd, [tokens[i], tokens[i+1]]))
            i += 2
        elif cmd == 'L' or cmd == 'l':  # 线段命令
            commands.append((cmd, [tokens[i], tokens[i+1]]))
            i += 2
        elif cmd == 'H' or cmd == 'h':  # 水平线命令
            commands.append((cmd, [tokens[i]]))
            i += 1
        elif cmd == 'V' or cmd == 'v':  # 垂直线命令
            commands.append((cmd, [tokens[i]]))
            i += 1
        elif cmd == 'C' or cmd == 'c':  # 三次贝塞尔曲线
            commands.append((cmd, [tokens[i], tokens[i+1], tokens[i+2], tokens[i+3], tokens[i+4], tokens[i+5]]))
            i += 6
        elif cmd == 'S' or cmd == 's':  # 平滑三次贝塞尔曲线
            commands.append((cmd, [tokens[i], tokens[i+1], tokens[i+2], tokens[i+3]]))
            i += 4
        elif cmd == 'Q' or cmd == 'q':  # 二次贝塞尔曲线
            commands.append((cmd, [tokens[i], tokens[i+1], tokens[i+2], tokens[i+3]]))
            i += 4
        elif cmd == 'T' or cmd == 't':  # 平滑二次贝塞尔曲线
            commands.append((cmd, [tokens[i], tokens[i+1]]))
            i += 2
        elif cmd == 'A' or cmd == 'a':  # 椭圆弧
            commands.append((cmd, [tokens[i], tokens[i+1], tokens[i+2], tokens[i+3], tokens[i+4], tokens[i+5], tokens[i+6]]))
            i += 7
        elif cmd == 'Z' or cmd == 'z':  # 闭合路径
            commands.append((cmd, []))
    
    return commands

def convert_to_absolute(commands):
    """将相对坐标转换为绝对坐标"""
    current_x, current_y = 0, 0
    start_x, start_y = 0, 0
    absolute_commands = []
    
    for cmd, params in commands:
        if cmd == 'M':  # 绝对移动
            current_x, current_y = params
            start_x, start_y = current_x, current_y
            absolute_commands.append(('M', params))
        elif cmd == 'm':  # 相对移动
            current_x += params[0]
            current_y += params[1]
            start_x, start_y = current_x, current_y
            absolute_commands.append(('M', [current_x, current_y]))
        elif cmd == 'L':  # 绝对线段
            current_x, current_y = params
            absolute_commands.append(('L', params))
        elif cmd == 'l':  # 相对线段
            current_x += params[0]
            current_y += params[1]
            absolute_commands.append(('L', [current_x, current_y]))
        elif cmd == 'H':  # 绝对水平线
            current_x = params[0]
            absolute_commands.append(('L', [current_x, current_y]))
        elif cmd == 'h':  # 相对水平线
            current_x += params[0]
            absolute_commands.append(('L', [current_x, current_y]))
        elif cmd == 'V':  # 绝对垂直线
            current_y = params[0]
            absolute_commands.append(('L', [current_x, current_y]))
        elif cmd == 'v':  # 相对垂直线
            current_y += params[0]
            absolute_commands.append(('L', [current_x, current_y]))
        elif cmd == 'C':  # 绝对三次贝塞尔曲线
            current_x, current_y = params[4], params[5]
            absolute_commands.append(('C', params))
        elif cmd == 'c':  # 相对三次贝塞尔曲线
            x1, y1 = current_x + params[0], current_y + params[1]
            x2, y2 = current_x + params[2], current_y + params[3]
            x, y = current_x + params[4], current_y + params[5]
            current_x, current_y = x, y
            absolute_commands.append(('C', [x1, y1, x2, y2, x, y]))
        elif cmd == 'S':  # 绝对平滑三次贝塞尔曲线
            current_x, current_y = params[2], params[3]
            absolute_commands.append(('S', params))
        elif cmd == 's':  # 相对平滑三次贝塞尔曲线
            x2, y2 = current_x + params[0], current_y + params[1]
            x, y = current_x + params[2], current_y + params[3]
            current_x, current_y = x, y
            absolute_commands.append(('S', [x2, y2, x, y]))
        elif cmd == 'Q':  # 绝对二次贝塞尔曲线
            current_x, current_y = params[2], params[3]
            absolute_commands.append(('Q', params))
        elif cmd == 'q':  # 相对二次贝塞尔曲线
            x1, y1 = current_x + params[0], current_y + params[1]
            x, y = current_x + params[2], current_y + params[3]
            current_x, current_y = x, y
            absolute_commands.append(('Q', [x1, y1, x, y]))
        elif cmd == 'T':  # 绝对平滑二次贝塞尔曲线
            current_x, current_y = params
            absolute_commands.append(('T', params))
        elif cmd == 't':  # 相对平滑二次贝塞尔曲线
            x, y = current_x + params[0], current_y + params[1]
            current_x, current_y = x, y
            absolute_commands.append(('T', [x, y]))
        elif cmd == 'A':  # 绝对椭圆弧
            current_x, current_y = params[5], params[6]
            absolute_commands.append(('A', params))
        elif cmd == 'a':  # 相对椭圆弧
            rx, ry, x_axis_rotation, large_arc_flag, sweep_flag = params[0], params[1], params[2], params[3], params[4]
            x, y = current_x + params[5], current_y + params[6]
            current_x, current_y = x, y
            absolute_commands.append(('A', [rx, ry, x_axis_rotation, large_arc_flag, sweep_flag, x, y]))
        elif cmd == 'Z' or cmd == 'z':  # 闭合路径
            current_x, current_y = start_x, start_y
            absolute_commands.append(('Z', []))
    
    return absolute_commands

def commands_to_path(commands):
    """将命令列表转换回路径字符串"""
    path = []
    for cmd, params in commands:
        path.append(cmd)
        if cmd == 'Z' or cmd == 'z':
            continue
        for param in params:
            path.append(str(param))
    
    # 格式化路径字符串
    formatted_path = ""
    i = 0
    while i < len(path):
        if path[i] in "MLHVCSQTAZmlhvcsqtaz":
            formatted_path += path[i] + " "
            i += 1
        else:
            formatted_path += path[i]
            i += 1
            if i < len(path) and path[i] not in "MLHVCSQTAZmlhvcsqtaz":
                formatted_path += " "
    
    return formatted_path

def apply_transform(x, y, transform_matrix):
    """应用变换矩阵到坐标"""
    # 变换矩阵: [a, b, c, d, e, f] 对应 [a c e; b d f; 0 0 1]
    a, b, c, d, e, f = transform_matrix
    new_x = a * x + c * y + e
    new_y = b * x + d * y + f
    return new_x, new_y

def parse_transform(transform_str):
    """解析变换字符串为变换矩阵"""
    if "scale" in transform_str and "translate" in transform_str:
        # 提取缩放和平移参数
        scale_match = re.search(r'scale\(([^)]+)\)', transform_str)
        translate_match = re.search(r'translate\(([^)]+)\)', transform_str)
        
        if scale_match and translate_match:
            scale_values = [float(val) for val in scale_match.group(1).split(',')]
            translate_values = [float(val) for val in translate_match.group(1).split(',')]
            
            # 假设scale(sx, sy) translate(tx, ty)
            sx = scale_values[0] if len(scale_values) > 0 else 1
            sy = scale_values[1] if len(scale_values) > 1 else sx
            
            tx = translate_values[0] if len(translate_values) > 0 else 0
            ty = translate_values[1] if len(translate_values) > 1 else 0
            
            # 返回变换矩阵 [a, b, c, d, e, f]
            return [sx, 0, 0, sy, tx, ty]
    
    # 如果是matrix形式
    matrix_match = re.search(r'matrix\(([^)]+)\)', transform_str)
    if matrix_match:
        return [float(val) for val in matrix_match.group(1).split(',')]
    
    # 如果只有translate
    translate_match = re.search(r'translate\(([^)]+)\)', transform_str)
    if translate_match:
        translate_values = [float(val) for val in translate_match.group(1).split(',')]
        tx = translate_values[0] if len(translate_values) > 0 else 0
        ty = translate_values[1] if len(translate_values) > 1 else 0
        return [1, 0, 0, 1, tx, ty]
    
    # 如果只有scale
    scale_match = re.search(r'scale\(([^)]+)\)', transform_str)
    if scale_match:
        scale_values = [float(val) for val in scale_match.group(1).split(',')]
        sx = scale_values[0] if len(scale_values) > 0 else 1
        sy = scale_values[1] if len(scale_values) > 1 else sx
        return [sx, 0, 0, sy, 0, 0]
    
    # 默认返回恒等变换
    return [1, 0, 0, 1, 0, 0]

def transform_elliptical_arc(rx, ry, x_axis_rotation, large_arc_flag, sweep_flag, x, y, transform_matrix):
    """完整处理椭圆弧变换"""
    # 提取变换矩阵的组件
    a, c, e = transform_matrix[0], transform_matrix[2], transform_matrix[4]
    b, d, f = transform_matrix[1], transform_matrix[3], transform_matrix[5]
    
    # 转换角度为弧度
    phi = math.radians(x_axis_rotation)
    
    # 计算变换后的椭圆参数
    # 这是一个复杂的数学过程，涉及到二次型的变换
    cos_phi = math.cos(phi)
    sin_phi = math.sin(phi)
    
    # 构建椭圆的二次型矩阵
    m11 = cos_phi / rx
    m12 = sin_phi / rx
    m21 = -sin_phi / ry
    m22 = cos_phi / ry
    
    # 应用变换
    m11_new = a * m11 + b * m21
    m12_new = a * m12 + b * m22
    m21_new = c * m11 + d * m21
    m22_new = c * m12 + d * m22
    
    # 从变换后的二次型矩阵中提取新的椭圆参数
    # 这里是简化版本，完整版本需要更复杂的计算
    A = m11_new * m11_new + m21_new * m21_new
    B = 2 * (m11_new * m12_new + m21_new * m22_new)
    C = m12_new * m12_new + m22_new * m22_new
    
    # 计算新的半径和旋转角度
    delta = B * B - 4 * A * C
    if abs(delta) < 1e-10:
        # 特殊情况处理
        new_rx = new_ry = math.sqrt(1 / A)
        new_x_axis_rotation = 0
    else:
        # 计算新的半径
        k = math.sqrt(abs(delta))
        new_rx = math.sqrt(2 / abs(A + C + k))
        new_ry = math.sqrt(2 / abs(A + C - k))
        
        # 计算新的旋转角度
        new_x_axis_rotation = math.degrees(0.5 * math.atan2(B, A - C))
    
    # 处理反射变换对 sweep_flag 的影响
    det = a * d - b * c
    new_sweep_flag = sweep_flag
    if det < 0:
        new_sweep_flag = 1 - sweep_flag
    
    # 变换终点坐标
    new_x = a * x + c * y + e
    new_y = b * x + d * y + f
    
    return new_rx, new_ry, new_x_axis_rotation, large_arc_flag, new_sweep_flag, new_x, new_y


def transform_path_commands(commands, transform_matrix):
    """应用变换矩阵到路径命令"""
    transformed_commands = []
    
    for cmd, params in commands:
        if cmd == 'M' or cmd == 'L':
            x, y = params
            new_x, new_y = apply_transform(x, y, transform_matrix)
            transformed_commands.append((cmd, [new_x, new_y]))
        elif cmd == 'C':
            x1, y1 = params[0], params[1]
            x2, y2 = params[2], params[3]
            x, y = params[4], params[5]
            
            new_x1, new_y1 = apply_transform(x1, y1, transform_matrix)
            new_x2, new_y2 = apply_transform(x2, y2, transform_matrix)
            new_x, new_y = apply_transform(x, y, transform_matrix)
            
            transformed_commands.append((cmd, [new_x1, new_y1, new_x2, new_y2, new_x, new_y]))
        elif cmd == 'S' or cmd == 'Q':
            x2, y2 = params[0], params[1]
            x, y = params[2], params[3]
            
            new_x2, new_y2 = apply_transform(x2, y2, transform_matrix)
            new_x, new_y = apply_transform(x, y, transform_matrix)
            
            transformed_commands.append((cmd, [new_x2, new_y2, new_x, new_y]))
        elif cmd == 'T':
            x, y = params
            new_x, new_y = apply_transform(x, y, transform_matrix)
            transformed_commands.append((cmd, [new_x, new_y]))
        elif cmd == 'A':
            # 椭圆弧需要特殊处理，这里简化处理
            # 可以使用函数 transform_elliptical_arc 优化
            # rx, ry = params[0], params[1]
            # x_axis_rotation = params[2]
            # large_arc_flag, sweep_flag = params[3], params[4]
            # x, y = params[5], params[6]
            
            # # 变换半径（简化，只考虑缩放）
            # new_rx = rx * abs(transform_matrix[0])
            # new_ry = ry * abs(transform_matrix[3])
            
            # # 变换终点
            # new_x, new_y = apply_transform(x, y, transform_matrix)
            
            # transformed_commands.append((cmd, [new_rx, new_ry, x_axis_rotation, large_arc_flag, sweep_flag, new_x, new_y]))
            transformed_commands.append((cmd, transform_elliptical_arc(*params, transform_matrix)))
            
        elif cmd == 'Z':
            transformed_commands.append((cmd, []))
    
    return transformed_commands

def convert_svg(svg_content):
    """转换SVG内容，消除transform并将相对坐标转为绝对坐标"""
    # 解析SVG
    root = ET.fromstring(svg_content)
    
    # 获取SVG命名空间
    ns = {'svg': 'http://www.w3.org/2000/svg'}
    
    # 查找所有带有transform属性的g元素
    for g in root.findall('.//svg:g[@transform]', ns):
        transform_str = g.get('transform')
        transform_matrix = parse_transform(transform_str)
        
        # 处理g元素下的所有path
        for path in g.findall('.//svg:path', ns):
            d = path.get('d')
            if d:
                # 解析路径
                commands = parse_path(d)
                
                # 转换为绝对坐标
                absolute_commands = convert_to_absolute(commands)
                
                # 应用变换
                transformed_commands = transform_path_commands(absolute_commands, transform_matrix)
                
                # 转换回路径字符串
                new_d = commands_to_path(transformed_commands)
                
                # 更新路径
                path.set('d', new_d)
        
        # 移除transform属性
        g.attrib.pop('transform')
    
    # 将SVG转换回字符串
    return ET.tostring(root, encoding='unicode')