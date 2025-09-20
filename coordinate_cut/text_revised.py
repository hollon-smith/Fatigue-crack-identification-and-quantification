def multiply_values_in_txt(input_file, output_file, multiplier=0.012537):
    """
    将文本文件中的所有数值乘以指定乘数

    参数:
        input_file: 输入文件路径
        output_file: 输出文件路径
        multiplier: 乘数(默认为0.05153)
    """
    try:
        with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
            for line in infile:
                # 处理每行内容
                parts = line.strip().split(',')
                processed_parts = []

                for part in parts:
                    try:
                        # 尝试将部分转换为浮点数并乘以乘数
                        num = float(part)
                        processed_num = num * multiplier
                        processed_parts.append(f"{processed_num:.6f}")  # 保留6位小数
                    except ValueError:
                        # 如果不能转换为数字，保持原样
                        processed_parts.append(part)

                # 将处理后的部分写回文件
                outfile.write(','.join(processed_parts) + '\n')

        print(f"处理完成！结果已保存到 {output_file}")

    except FileNotFoundError:
        print(f"错误：找不到输入文件 {input_file}")
    except Exception as e:
        print(f"处理文件时出错: {str(e)}")


if __name__ == "__main__":
    # 输入文件路径（替换为你的实际文件路径）
    input_txt = r"E:\pycharm_programs\coordinate_cut\DH\11_revised_skeleton_points.txt"

    # 输出文件路径（在原文件名基础上添加_scaled后缀）
    import os

    base, ext = os.path.splitext(input_txt)
    output_txt = f"{base}_scaled{ext}"

    # 执行处理
    multiply_values_in_txt(input_txt, output_txt)

    # 等待用户按Enter键退出
    input("按Enter键退出...")