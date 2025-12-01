import re

# 读取SVG文件
with open('../svg_pic/8.svg', 'r', encoding='utf-8') as f:
    svg_content = f.read()

# 修复路径数据：在数字和小写v命令之间加上空格
# 注意：我们只修复路径数据中的问题，所以只针对d属性
def fix_path_data(match):
    path_data = match.group(1)
    # 使用正则表达式在数字和v之间插入空格
    # 注意：要避免在科学计数法中的e或E，但这里是小写v，所以没关系
    fixed_path_data = re.sub(r'(\d)(v)', r'\1 \2', path_data)
    return 'd="{}"'.format(fixed_path_data)

# 使用正则表达式匹配所有d属性
svg_content = re.sub(r'd="([^"]*)"', fix_path_data, svg_content)

# 保存修复后的文件
with open('your_file_fixed.svg', 'w', encoding='utf-8') as f:
    f.write(svg_content)