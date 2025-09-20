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

def select_endpoints(points, origin, x_dir, y_dir, interval=200):
    """
    使用点击定义的坐标系，计算每个骨架点在该坐标系下的 (x', y')，并每 interval 选取一个端点
    确保末端点也被记录
    """
    if len(points) == 0:
        return []

    # 计算所有点在新坐标系下的投影
    transformed = []
    for x, y in points:
        vec = np.array([x, y]) - origin
        x_new = np.dot(vec, x_dir)
        y_new = np.dot(vec, y_dir)
        transformed.append((x_new, y_new))

    # 按 x_new 排序
    transformed.sort(key=lambda p: p[0])

    selected = []
    last_selected_x = -1e9  # 初始化为足够小，保证第一个点被选

    for x_new, y_new in transformed:
        if x_new - last_selected_x >= interval:
            selected.append((x_new, y_new))
            last_selected_x = x_new

    # 确保末端也记录
    if len(selected) == 0 or transformed[-1] != selected[-1]:
        selected.append(transformed[-1])

    return selected


def draw_points_on_image(img, points, origin, x_dir, y_dir):
    """
    在图像上绘制端点坐标
    """
    img_color = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    for (dx, dy) in points:
        # 将 (dx, dy) 转回图像坐标系显示
        point = origin + dx * x_dir + dy * y_dir
        x, y = int(round(point[0])), int(round(point[1]))
        cv2.circle(img_color, (x, y), 3, (0,0,255), -1)  # 红色小圆
        text = f"({int(dx)},{int(dy)})"
        cv2.putText(img_color, text, (x+5, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,255,0), 1)

    return img_color

def save_points_txt(points, save_txt_path):
    with open(save_txt_path, 'w') as f:
        for (dx, dy) in points:
            f.write(f"{dx},{dy}\n")
    print(f"坐标已保存至 {save_txt_path}")

def define_coordinate_system(rgb_img):
    clicks = []

    fig, ax = plt.subplots()
    ax.imshow(rgb_img)
    title = ax.set_title('Step 1: Click origin point')

    def onclick(event):
        if event.xdata is not None and event.ydata is not None:
            x, y = event.xdata, event.ydata
            clicks.append((x, y))
            print(f"Clicked: ({x:.2f}, {y:.2f})")

            if len(clicks) == 1:
                ax.plot(x, y, 'ro', markersize=8)
                title.set_text('Step 2: Click x-axis direction point')
                fig.canvas.draw()

            elif len(clicks) == 2:
                origin = np.array(clicks[0])
                x_dir_point = np.array(clicks[1])
                ax.plot([origin[0], x_dir_point[0]], [origin[1], x_dir_point[1]], 'r-', linewidth=2)
                ax.plot(x_dir_point[0], x_dir_point[1], 'bo', markersize=8)
                title.set_text('Coordinate system defined. Close window to continue.')
                fig.canvas.draw()
                plt.disconnect(cid)

    cid = plt.connect('button_press_event', onclick)
    plt.show()

    if len(clicks) < 2:
        raise ValueError("未完成坐标系点击，请重试。")

    origin = np.array(clicks[0])
    x_dir = np.array(clicks[1]) - origin
    x_dir = x_dir / np.linalg.norm(x_dir)
    y_dir = np.array([-x_dir[1], x_dir[0]])  # 右手系：x 逆时针旋转90°

    # 不进行单位缩放，坐标值即为像素差值

    return origin, x_dir, y_dir


def click_two_points_and_measure_distance(rgb_img):
    """
    显示图像，点击两点，计算像素距离
    """
    clicks = []

    fig, ax = plt.subplots()
    ax.imshow(rgb_img)
    title = ax.set_title('Click two points to measure distance')

    def onclick(event):
        if event.xdata is not None and event.ydata is not None:
            x, y = event.xdata, event.ydata
            clicks.append((x, y))
            ax.plot(x, y, 'ro', markersize=8)
            fig.canvas.draw()
            print(f"Clicked: ({x:.2f}, {y:.2f})")
            if len(clicks) == 2:
                plt.disconnect(cid)
                title.set_text('Two points selected. Close window to continue.')

    cid = plt.connect('button_press_event', onclick)
    plt.show()

    if len(clicks) < 2:
        raise ValueError("未点击两点，请重试。")

    # 计算欧氏距离
    p1 = np.array(clicks[0])
    p2 = np.array(clicks[1])
    distance = np.linalg.norm(p2 - p1)
    print(f"两点之间的像素距离为: {distance:.2f}")

    return distance

# 其余函数 extract_skeleton, get_skeleton_points, select_endpoints, draw_points_on_image,
# save_points_txt, define_coordinate_system 与之前保持一致，这里省略

def main(rgb_img_path, mask_img_path, save_img_path, save_txt_path):
    # 读取 RGB 原图
    rgb_img = cv2.cvtColor(cv2.imread(rgb_img_path), cv2.COLOR_BGR2RGB)
    height, width = rgb_img.shape[:2]

    # 【新增功能】点击两点计算像素距离
    distance = click_two_points_and_measure_distance(rgb_img)
    # 如果需要，可将 distance 保存或用于后续计算

    # 1. 手动点击建立坐标系
    origin, x_dir, y_dir = define_coordinate_system(rgb_img)

    # 2. 读取 mask 二值图，并resize到RGB图尺寸
    binary_img = cv2.imread(mask_img_path, cv2.IMREAD_GRAYSCALE)
    binary_img_resized = cv2.resize(binary_img, (width, height), interpolation=cv2.INTER_NEAREST)
    _, binary_img_resized = cv2.threshold(binary_img_resized, 127, 255, cv2.THRESH_BINARY)

    # 3. 骨架化
    skeleton = extract_skeleton(binary_img)

    # 4. 提取骨架点
    points = get_skeleton_points(skeleton)

    # 5. 每interval选取端点（使用坐标系转换）
    selected_points = select_endpoints(points, origin, x_dir, y_dir, interval=200)

    # 6. 在图像上绘制端点
    img_with_points = draw_points_on_image(skeleton, selected_points, origin, x_dir, y_dir)

    # 7. 保存结果
    cv2.imwrite(save_img_path, img_with_points)
    print(f"结果图像已保存至 {save_img_path}")

    save_points_txt(selected_points, save_txt_path)

    # 8. 可视化
    plt.figure(figsize=(10,5))
    plt.imshow(cv2.cvtColor(img_with_points, cv2.COLOR_BGR2RGB))
    plt.title("Skeleton with Endpoints in Custom Coordinate System")
    plt.axis('off')
    plt.show()

if __name__ == '__main__':
    rgb_img_path = r"C:\Users\GHB\Desktop\test_dataset\TransUNet\frame_00252.jpg"
    mask_img_path = r"C:\Users\GHB\Desktop\test_dataset\TransUNet\frame_00252_main_skeleton.JPG"
    save_img_path = r"C:\Users\GHB\Desktop\test_dataset\TransUNet\frame_00252_with_points.png"
    save_txt_path = r"C:\Users\GHB\Desktop\test_dataset\TransUNet\frame_00252_points.txt"

    main(rgb_img_path, mask_img_path, save_img_path, save_txt_path)
