import cv2
import numpy as np
import matplotlib.pyplot as plt
from skimage.morphology import skeletonize
from scipy.interpolate import splprep, splev

# ===============================
# 1. 读取图像
# ===============================
img_path = r"C:\Users\GHB\Desktop\test_dataset\HH_hole-110.JPG"
img = cv2.imread(img_path)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# ===============================
# 2. 预处理
# ===============================
blur = cv2.GaussianBlur(gray, (5, 5), 0)

# ===============================
# 3. 边缘检测
# ===============================
edges = cv2.Canny(blur, 50, 150)

# ===============================
# 4. 骨架化
# ===============================
skeleton = skeletonize(edges > 0)

# 提取骨架点坐标
ys, xs = np.where(skeleton)
points = np.array(list(zip(xs, ys)))

# ===============================
# 5. B样条拟合
# ===============================
if len(points) >= 4:  # B样条至少需要4个点
    # 按x排序（假设横向为主轴）
    points = points[np.argsort(points[:,0])]

    # 参数 tck 为 (t, c, k)，u 为参数化结果
    tck, u = splprep([points[:,0], points[:,1]], s=5)  # s 为平滑因子
    unew = np.linspace(0, 1.0, num=500)
    out = splev(unew, tck)

    # 绘制结果
    plt.figure(figsize=(10,6))
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    plt.plot(points[:,0], points[:,1], 'r.', label='Skeleton points')
    plt.plot(out[0], out[1], 'b-', linewidth=2, label='B-spline curve')
    plt.legend()
    plt.title("U-rib & Crossbeam Intersection Curve Extraction")
    plt.show()

    # 保存拟合点
    np.savetxt("intersection_curve_points.txt", np.vstack(out).T, fmt="%.2f", delimiter=",")
    print("拟合曲线坐标已保存：intersection_curve_points.txt")
else:
    print("骨架点数量不足，无法拟合B样条")
