import pandas as pd
import numpy as np

# 直线参数
k = 0.04255
b = 0.18810
A, B, C = k, -1, b

# 1. 读取Excel文件 (假设前两列是 x, y 坐标)
df = pd.read_excel(r"C:\Users\GHB\Desktop\crack_left.xlsx")
x = df.iloc[:, 0].to_numpy()
y = df.iloc[:, 1].to_numpy()

# 2. 计算点到直线的距离
distances = np.abs(A * x + B * y + C) / np.sqrt(A**2 + B**2)

# 3. 保存点到直线的距离
with open("point_line_distances_left.txt", "w", encoding="utf-8") as f:
    for i, d in enumerate(distances):
        f.write(f"Point {i+1}: {d:.6f}\n")

# 4. 计算每段折线与直线的夹角
line_vec = np.array([1, k])
line_vec_norm = np.linalg.norm(line_vec)

angles = []
for i in range(len(x) - 1):
    seg_vec = np.array([x[i+1] - x[i], y[i+1] - y[i]])
    seg_norm = np.linalg.norm(seg_vec)
    if seg_norm == 0:
        angle_deg = np.nan  # 避免除零错误
    else:
        dot_product = np.dot(seg_vec, line_vec)
        cos_theta = dot_product / (seg_norm * line_vec_norm)
        cos_theta = np.clip(cos_theta, -1, 1)  # 避免数值误差导致超出 [-1, 1]
        angle_deg = np.degrees(np.arccos(cos_theta))
    angles.append(angle_deg)

# 5. 保存夹角到新文件
with open("polyline_line_angles_left.txt", "w", encoding="utf-8") as f:
    for i, angle in enumerate(angles):
        if np.isnan(angle):
            f.write(f"Segment {i+1}: 无法计算（两点重合）\n")
        else:
            f.write(f"Segment {i+1}: {angle:.6f}°\n")

print(f"✅ 点到直线的距离已保存到 point_line_distances_1.txt")
print(f"✅ 每段折线与直线的夹角已保存到 polyline_line_angles.txt")
