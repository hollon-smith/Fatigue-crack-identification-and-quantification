import cv2
import numpy as np
from skimage.morphology import skeletonize
import matplotlib.pyplot as plt

def extract_skeleton(binary_img):
    skeleton = skeletonize(binary_img // 255)
    skeleton = (skeleton * 255).astype(np.uint8)
    return skeleton

def get_skeleton_points(skeleton_img):
    ys, xs = np.where(skeleton_img > 0)
    points = list(zip(xs, ys))
    return points

def select_endpoints(points, interval=200):
    """
    以骨架最左端点为(0,0)，每interval划分节段
    """
    if len(points) == 0:
        return []

    # 以 x 坐标排序，找到最左端点作为 (0,0)
    points.sort(key=lambda p: p[0])
    x0, y0 = points[0]

    # 坐标平移
    transformed = [(x - x0, y - y0) for x, y in points]

    # 按 x_new 排序
    transformed.sort(key=lambda p: p[0])

    selected = []
    last_selected_x = -1e9

    for x_new, y_new in transformed:
        if x_new - last_selected_x >= interval:
            selected.append((x_new, y_new))
            last_selected_x = x_new

    # 确保末端点也记录
    if len(selected) == 0 or transformed[-1] != selected[-1]:
        selected.append(transformed[-1])

    return selected, (x0, y0)

def draw_points_on_image(img, points, offset):
    """
    在图像上绘制端点坐标 (以最左端点为0,0)
    """
    img_color = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    x0, y0 = offset

    for (dx, dy) in points:
        x, y = int(round(dx + x0)), int(round(dy + y0))
        cv2.circle(img_color, (x, y), 3, (0,0,255), -1)
        text = f"({int(dx)},{int(dy)})"
        cv2.putText(img_color, text, (x+5, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,255,0), 1)

    return img_color

def save_points_txt(points, save_txt_path):
    with open(save_txt_path, 'w') as f:
        for (dx, dy) in points:
            f.write(f"{dx},{dy}\n")
    print(f"坐标已保存至 {save_txt_path}")

def main(mask_img_path, save_img_path, save_txt_path):
    # 读取 mask 二值图
    binary_img = cv2.imread(mask_img_path, cv2.IMREAD_GRAYSCALE)
    _, binary_img = cv2.threshold(binary_img, 127, 255, cv2.THRESH_BINARY)

    # 骨架化
    skeleton = extract_skeleton(binary_img)

    # 提取骨架点
    points = get_skeleton_points(skeleton)

    # 每interval选取端点（以骨架左端点为原点）
    selected_points, offset = select_endpoints(points, interval=200)

    # 在图像上绘制端点
    img_with_points = draw_points_on_image(skeleton, selected_points, offset)

    # 保存结果
    cv2.imwrite(save_img_path, img_with_points)
    print(f"结果图像已保存至 {save_img_path}")

    save_points_txt(selected_points, save_txt_path)

    # 可视化
    plt.figure(figsize=(10,5))
    plt.imshow(cv2.cvtColor(img_with_points, cv2.COLOR_BGR2RGB))
    plt.title("Skeleton with Endpoints (Origin at Leftmost Point)")
    plt.axis('off')
    plt.show()

if __name__ == '__main__':
    mask_img_path = r"C:\Users\GHB\Desktop\test_dataset\u2net\HH_hole-110_connected.jpg"
    save_img_path = r"C:\Users\GHB\Desktop\test_dataset\u2net\HH_hole-110_with_points.png"
    save_txt_path = r"C:\Users\GHB\Desktop\test_dataset\u2net\HH_hole-110_points.txt"

    main(mask_img_path, save_img_path, save_txt_path)
