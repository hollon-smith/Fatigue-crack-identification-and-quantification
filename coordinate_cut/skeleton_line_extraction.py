import cv2
import numpy as np
from skimage.morphology import skeletonize
import matplotlib.pyplot as plt
import networkx as nx

def extract_skeleton(binary_img):
    skeleton = skeletonize(binary_img // 255)
    skeleton = (skeleton * 255).astype(np.uint8)
    return skeleton

def connect_by_column_search(skeleton_img, max_search_cols=50):
    connected = skeleton_img.copy()
    rows, cols = skeleton_img.shape

    last_ys = None
    col = 0
    while col < cols:
        ys = np.where(skeleton_img[:, col] > 0)[0]

        if len(ys) > 0:
            if last_ys is None:
                last_ys = ys
                col_prev = col
            else:
                for last_y in last_ys:
                    diffs = np.abs(ys - last_y)
                    idx_min = np.argmin(diffs)
                    y_current = ys[idx_min]
                    cv2.line(connected, (col_prev, last_y), (col, y_current), 255, 1)
                last_ys = ys
                col_prev = col
            col += 1

        else:
            found = False
            for offset in range(1, max_search_cols+1):
                next_col = col + offset
                if next_col >= cols:
                    break
                ys_next = np.where(skeleton_img[:, next_col] > 0)[0]
                if len(ys_next) > 0:
                    if last_ys is not None:
                        for last_y in last_ys:
                            diffs = np.abs(ys_next - last_y)
                            idx_min = np.argmin(diffs)
                            y_next = ys_next[idx_min]
                            cv2.line(connected, (col_prev, last_y), (next_col, y_next), 255, 1)
                    last_ys = ys_next
                    col_prev = next_col
                    col = next_col
                    found = True
                    break
            if not found:
                last_ys = None
                col += 1

    return connected

def skeleton_to_graph(skeleton_img):
    G = nx.Graph()
    h, w = skeleton_img.shape
    for y in range(h):
        for x in range(w):
            if skeleton_img[y, x] > 0:
                G.add_node((x, y))
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue
                        nx_, ny_ = x + dx, y + dy
                        if 0 <= nx_ < w and 0 <= ny_ < h and skeleton_img[ny_, nx_] > 0:
                            G.add_edge((x, y), (nx_, ny_))
    return G

def find_endpoints(G):
    return [node for node, degree in G.degree() if degree == 1]

def extract_longest_path(G):
    endpoints = find_endpoints(G)
    longest_path = []
    max_length = 0

    for i in range(len(endpoints)):
        for j in range(i+1, len(endpoints)):
            try:
                path = nx.shortest_path(G, endpoints[i], endpoints[j])
                if len(path) > max_length:
                    max_length = len(path)
                    longest_path = path
            except nx.NetworkXNoPath:
                continue

    return longest_path

def save_longest_path_as_image(shape, path, save_path):
    """
    创建与原图同尺寸的空白图，仅绘制主骨架线（白色），背景黑色
    """
    img = np.zeros(shape, dtype=np.uint8)
    for (x, y) in path:
        img[y, x] = 255
    cv2.imwrite(save_path, img)
    print(f"主骨架线二值图已保存至 {save_path}")
    return img

def main(input_binary_crack_img, save_connected_path, save_longest_path_img):
    # 1. 骨架化
    skeleton = extract_skeleton(input_binary_crack_img)

    # 2. 逐列搜索连接断裂
    connected = connect_by_column_search(skeleton, max_search_cols=50)
    cv2.imwrite(save_connected_path, connected)
    print(f"断裂修复后骨架已保存至 {save_connected_path}")

    # 3. 提取主骨架线
    G = skeleton_to_graph(connected)
    longest_path = extract_longest_path(G)
    print(f"最长主骨架线长度: {len(longest_path)}")

    # 4. 创建主骨架线二值图
    longest_path_img = save_longest_path_as_image(connected.shape, longest_path, save_longest_path_img)

    # 5. 可视化对比
    plt.figure(figsize=(15,5))
    plt.subplot(1,3,1)
    plt.title("Original Skeleton")
    plt.imshow(skeleton, cmap='gray')
    plt.axis('off')

    plt.subplot(1,3,2)
    plt.title("Connected Skeleton")
    plt.imshow(connected, cmap='gray')
    plt.axis('off')

    plt.subplot(1,3,3)
    plt.title("Main Skeleton Line")
    plt.imshow(longest_path_img, cmap='gray')
    plt.axis('off')

    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    img_path = r"E:\pycharm_programs\coordinate_cut\DH\11.png"
    save_connected_path = r"E:\pycharm_programs\coordinate_cut\DH\11_connected.jpg"
    save_longest_path_img = r"E:\pycharm_programs\coordinate_cut\DH\11_revised_skeleton.jpg"

    binary_img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    if binary_img is None:
        print("请确认路径和图像是否正确")
    else:
        _, binary_img = cv2.threshold(binary_img, 127, 255, cv2.THRESH_BINARY)
        main(binary_img, save_connected_path, save_longest_path_img)
