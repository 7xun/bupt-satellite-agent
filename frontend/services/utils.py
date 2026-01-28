
# 这是之前的版本，存在一些问题

def extract_file_path(text, ext_pattern):
    """
    从文本中提取有效的文件路径。
    支持绝对路径、相对路径和文件名。
    """
    import re, os
    pattern = rf"""
        (?:[a-zA-Z]:[\\/]|/)             # Windows 盘符或 POSIX 根目录
        (?:[^\s<>:"|?*]+[\\/])*          # 目录片段
        [^\s<>:"|?*]+\.{ext_pattern}     # 文件名
        |
        (?:[\w\-.]+[\\/])*[\w\-.]+\.{ext_pattern}
    """
    matches = re.finditer(pattern, text, re.IGNORECASE | re.VERBOSE)

    for match in matches:
        path = match.group(0).strip().strip('`"\'')
        if os.path.exists(path):
            return path
        abs_path = os.path.abspath(path)
        if os.path.exists(abs_path):
            return abs_path

    return None



# # 上一版有问题，这一版也未必完美
# def extract_file_path(text, ext_pattern):
#     """
#     从文本中提取有效的文件路径。
#     支持绝对路径、相对路径和文件名。
#     """
#     import re, os
    
#     # 更灵活的正则表达式
#     # 支持：字母、数字、下划线、连字符、点、空格、#、@、$、%、^、&、+、=、~等
#     pattern = rf"""
#         (?:[a-zA-Z]:[\/])?            # 非捕获分组：可选的驱动器号 C: 或 C:\
#         (?:                             # 非捕获分组开始（目录部分）
#             [^\/:*?"<>|\r\n]+         # 字符类：除了\/:*?"<>|和换行符的任意字符
#             [\/]                      # 字符类：匹配\或/
#         )*                             # 前面的分组重复0次或多次
#         [^\/:*?"<>|\r\n]+             # 字符类：文件名（不含扩展名）
#         \.{ext_pattern}                # 匹配点号 + 扩展名
#     """
    
#     matches = re.findall(pattern, text, re.IGNORECASE | re.VERBOSE)
    
#     for match in matches:
#         path = match.strip()
#         # 清理可能的引导/结尾符号
#         path = path.strip('`"\'')
        
#         # 尝试查找文件
#         if os.path.exists(path):
#             return path
        
#         # 对于Windows路径，尝试标准化
#         if '\\' in path:
#             normalized = os.path.normpath(path)
#             if os.path.exists(normalized):
#                 return normalized
            
#     return None
