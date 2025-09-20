import numpy as np

def triangle_vertex_coordinates(a, b, c):
    """
    计算已知三边长三角形的三个顶点坐标
    将边c放在x轴 (0,0)-(c,0) 上，求顶点坐标
    """
    # 顶点C坐标为 (0,0)，顶点B坐标为 (c,0)
    # 求顶点A坐标 (x, y)
    x = (a**2 + c**2 - b**2) / (2 * c)
    y_square = a**2 - x**2
    if y_square < 0:
        raise ValueError("三角形三边长不满足三角不等式")
    y = np.sqrt(y_square)
    return (0,0), (c,0), (x,y)

def point_to_vertex_distance_on_edge(c, x_t, y_t, positions):
    """
    计算边c上不同位置点到对角顶点的距离
    positions: 边c上的点的x坐标数组
    """
    distances = []
    for x_p in positions:
        dx = x_t - x_p
        dy = y_t - 0
        d = np.sqrt(dx**2 + dy**2)
        distances.append(d)
    return distances

if __name__ == "__main__":
    a = 11.6
    b = 18.16
    c = 15.466

    # 求三角形顶点坐标
    A, B, C = triangle_vertex_coordinates(a, b, c)
    x_t, y_t = C

    print(f"顶点坐标: ({x_t:.3f}, {y_t:.3f})")

    # 生成边c上每1单位的点
    positions = [3.192487901,
3.573727984,
1.328293909,
3.66283251,
3.185486831,
6.670746749,
3.879865679,
6.985158436,
6.712116708,
2.715142222,
4.308203868
]

    # 计算这些点到顶点的距离
    distances = point_to_vertex_distance_on_edge(c, x_t, y_t, positions)

    for x_p, d in zip(positions, distances):
        print(f"位置 x={x_p:.3f} : 距离 = {d:.3f}")
