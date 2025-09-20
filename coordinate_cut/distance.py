import pandas as pd
import numpy as np

# 直线参数
k = 0.04255
b = 0.18810
A, B, C = k, -1, b

# 1. 读取Excel文件 (假设前两列是 x, y 坐标)
df = pd.read_excel(r"C:\Users\GHB\Desktop\crack_right.xlsx")
x = df.iloc[:, 0].to_numpy()
y = df.iloc[:, 1].to_numpy()

# 2. 计算点到直线的距离
distances = np.abs(A * x + B * y + C) / np.sqrt(A**2 + B**2)

# 3. 计算折线方向向量
polyline_vec = np.array([x[-1] - x[0], y[-1] - y[0]])
line_vec = np.array([1, k])

# 4. 计算夹角
dot_product = np.dot(polyline_vec, line_vec)
angle_rad = np.arccos(dot_product / (np.linalg.norm(polyline_vec) * np.linalg.norm(line_vec)))
angle_deg = np.degrees(angle_rad)

# 5. 保存结果
with open("point_line_distances_right.txt", "w", encoding="utf-8") as f:
    for i, d in enumerate(distances):
        f.write(f"Point {i+1}: {d:.6f}\n")
    f.write(f"\nPolyline vs Line Angle: {angle_deg:.6f}°\n")

print(f"✅ 点到直线的欧式距离已保存到 point_line_distances_2.txt")
print(f"✅ 折线与直线的夹角为 {angle_deg:.6f}°")

