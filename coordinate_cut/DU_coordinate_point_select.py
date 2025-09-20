import cv2
import numpy as np
from skimage.morphology import skeletonize
import matplotlib.pyplot as plt


def extract_skeleton(binary_img):
    skeleton = skeletonize(binary_img // 255)
    skeleton = (skeleton * 255).astype(np.uint8)
    return skeleton


def define_coordinate_system(rgb_img):
    height, width = rgb_img.shape[:2]
    origin_x = width // 2  # 自动设置原点在宽度中线
    clicks = []

    fig, ax = plt.subplots()
    ax.imshow(rgb_img)
    ax.axvline(x=origin_x, color='r', linestyle='--', linewidth=1)  # 显示中线
    title = ax.set_title('Step 1: Click y-axis direction point (origin is at center line)')

    def onclick(event):
        if event.xdata is not None and event.ydata is not None:
            y = event.ydata
            clicks.append(y)
            print(f"Clicked y-coordinate: {y:.2f}")

            if len(clicks) == 1:
                origin = np.array([origin_x, y])
                ax.plot(origin_x, y, 'ro', markersize=8)  # 标记原点
                title.set_text('Step 2: Click another point to define y-axis direction')
                fig.canvas.draw()

            elif len(clicks) == 2:
                origin_y = clicks[0]
                y_dir_point_y = clicks[1]

                # 原点在(origin_x, origin_y)
                origin = np.array([origin_x, origin_y])

                # y轴方向点直接在原点上方或下方
                y_dir_point = np.array([origin_x, y_dir_point_y])

                # y轴方向向量
                y_dir = y_dir_point - origin
                y_dir = y_dir / np.linalg.norm(y_dir)

                # x轴方向向量（与y轴垂直，右手系）
                x_dir = np.array([y_dir[1], -y_dir[0]])

                # 绘制坐标系
                ax.plot([origin[0], origin[0] + x_dir[0] * 50], [origin[1], origin[1] + x_dir[1] * 50], 'r-',
                        linewidth=2)
                ax.plot([origin[0], origin[0] + y_dir[0] * 50], [origin[1], origin[1] + y_dir[1] * 50], 'b-',
                        linewidth=2)
                ax.plot(origin[0] + x_dir[0] * 50, origin[1] + x_dir[1] * 50, 'ro', markersize=6)  # x轴端点
                ax.plot(origin[0] + y_dir[0] * 50, origin[1] + y_dir[1] * 50, 'bo', markersize=6)  # y轴端点

                title.set_text('Coordinate system defined. Close window to continue.')
                fig.canvas.draw()
                plt.disconnect(cid)

                # 保存坐标系参数
                define_coordinate_system.origin = origin
                define_coordinate_system.x_dir = x_dir
                define_coordinate_system.y_dir = y_dir

    cid = plt.connect('button_press_event', onclick)
    plt.show()

    if len(clicks) < 2:
        raise ValueError("未完成坐标系点击，请重试。")

    return define_coordinate_system.origin, define_coordinate_system.x_dir, define_coordinate_system.y_dir


def select_points_manually(img, origin, x_dir, y_dir):
    points = []

    fig, ax = plt.subplots()
    ax.imshow(img)
    title = ax.set_title('Click points to record coordinates. Close window when done.')

    def onclick(event):
        if event.xdata is not None and event.ydata is not None:
            x, y = event.xdata, event.ydata
            vec = np.array([x, y]) - origin
            dx = np.dot(vec, x_dir)
            dy = np.dot(vec, y_dir)
            points.append((dx, dy))
            print(f"Clicked: ({x:.2f}, {y:.2f}) --> (dx, dy)=({dx:.2f},{dy:.2f})")
            ax.plot(x, y, 'ro', markersize=5)
            ax.text(x + 5, y - 5, f"({int(dx)},{int(dy)})", color='green', fontsize=8)
            fig.canvas.draw()

    cid = plt.connect('button_press_event', onclick)
    plt.show()

    plt.disconnect(cid)
    return points


def draw_points_on_image(img, points, origin, x_dir, y_dir):
    img_color = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    for (dx, dy) in points:
        point = origin + dx * x_dir + dy * y_dir
        x, y = int(round(point[0])), int(round(point[1]))
        cv2.circle(img_color, (x, y), 3, (0, 0, 255), -1)
        text = f"({int(dx)},{int(dy)})"
        cv2.putText(img_color, text, (x + 5, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

    return img_color


def save_points_txt(points, save_txt_path):
    with open(save_txt_path, 'w') as f:
        for (dx, dy) in points:
            f.write(f"{dx},{dy}\n")
    print(f"坐标已保存至 {save_txt_path}")


def main(rgb_img_path, mask_img_path, save_img_path, save_txt_path):
    rgb_img = cv2.cvtColor(cv2.imread(rgb_img_path), cv2.COLOR_BGR2RGB)
    height, width = rgb_img.shape[:2]

    # 1. 定义坐标系（原点自动在宽度中线上）
    origin, x_dir, y_dir = define_coordinate_system(rgb_img)

    # 2. 读取并预处理二值图
    binary_img = cv2.imread(mask_img_path, cv2.IMREAD_GRAYSCALE)
    binary_img_resized = cv2.resize(binary_img, (width, height), interpolation=cv2.INTER_NEAREST)
    _, binary_img_resized = cv2.threshold(binary_img_resized, 127, 255, cv2.THRESH_BINARY)

    # 3. 骨架化
    skeleton = extract_skeleton(binary_img_resized)

    # 4. 手动选取点
    selected_points = select_points_manually(skeleton, origin, x_dir, y_dir)

    # 5. 绘制并保存
    img_with_points = draw_points_on_image(skeleton, selected_points, origin, x_dir, y_dir)
    cv2.imwrite(save_img_path, img_with_points)
    print(f"结果图像已保存至 {save_img_path}")

    save_points_txt(selected_points, save_txt_path)

    # 6. 显示结果
    plt.figure(figsize=(10, 5))
    plt.imshow(cv2.cvtColor(img_with_points, cv2.COLOR_BGR2RGB))
    plt.title("Skeleton with Manually Selected Points")
    plt.axis('off')
    plt.show()


if __name__ == '__main__':
    rgb_img_path = r"E:\pycharm_programs\coordinate_cut\DH\original_image.png"
    mask_img_path = r"E:\pycharm_programs\coordinate_cut\DH\11_revised_skeleton.jpg"
    save_img_path = r"E:\pycharm_programs\coordinate_cut\DH\11_revised_skeleton_with_points.png"
    save_txt_path = r"E:\pycharm_programs\coordinate_cut\DH\11_revised_skeleton_points.txt"

    main(rgb_img_path, mask_img_path, save_img_path, save_txt_path)