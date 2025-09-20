import numpy as np

def triangle_height(a, b, c):
    """
    计算已知三边长三角形，
    顶点到边c的垂直距离（高）
    """
    s = (a + b + c) / 2
    S_square = s * (s - a) * (s - b) * (s - c)
    if S_square < 0:
        raise ValueError("三角形三边长不满足三角不等式")
    S = np.sqrt(S_square)
    h = (2 * S) / c
    return h

if __name__ == "__main__":
    a = 11.6
    b = 18.16
    c = 15.466

    height = triangle_height(a, b, c)
    print(f"顶点到边c的垂直距离（高） = {height:.3f}")
