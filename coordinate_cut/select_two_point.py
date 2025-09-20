import matplotlib.pyplot as plt
import numpy as np


class PointSelector:
    def __init__(self, image):
        self.image = image
        self.fig, self.ax = plt.subplots()
        self.ax.imshow(self.image)
        self.points = []
        self.line = None
        self.text = None

        # 连接鼠标点击事件
        self.cid = self.fig.canvas.mpl_connect('button_press_event', self.on_click)

        plt.title("Click two points to measure distance")
        plt.show()

    def on_click(self, event):
        if event.inaxes != self.ax:
            return

        # 添加点
        self.points.append((event.xdata, event.ydata))
        self.ax.plot(event.xdata, event.ydata, 'ro')  # 绘制红点

        # 如果已经有两个点，计算距离
        if len(self.points) == 2:
            # 计算欧几里得距离
            p1, p2 = self.points
            distance = np.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)

            # 绘制线段
            if self.line:
                self.line.remove()
            self.line, = self.ax.plot([p1[0], p2[0]], [p1[1], p2[1]], 'b-')

            # 显示距离
            if self.text:
                self.text.remove()
            self.text = self.ax.text(0.02, 0.95,
                                     f"Distance: {distance:.2f} pixels",
                                     transform=self.ax.transAxes,
                                     color='green', fontsize=12,
                                     bbox=dict(facecolor='white', alpha=0.7))

            print(f"Pixel distance: {distance:.2f}")

            # 重置点列表
            self.points = []

        self.fig.canvas.draw()


# 使用示例
if __name__ == "__main__":
    # 读取图像 (替换为你的图像路径)
    from PIL import Image
    import requests
    from io import BytesIO

    from matplotlib.image import imread

    image_array = imread(r"E:\pycharm_programs\coordinate_cut\HH\HH_original-54.jpg")  # 替换为你的图像路径


    # 创建选择器实例
    selector = PointSelector(image_array)