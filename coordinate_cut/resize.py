import cv2
import os

def resize_mask_to_rgb(mask_path, rgb_path, save_path):
    """
    将 mask 图 resize 到 RGB 图尺寸，并保存
    """
    # 读取 RGB 图像，获取尺寸
    rgb_img = cv2.imread(rgb_path)
    if rgb_img is None:
        print("RGB 图像读取失败")
        return
    height, width = rgb_img.shape[:2]

    # 读取 mask 图像
    mask_img = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
    if mask_img is None:
        print("Mask 图像读取失败")
        return

    # resize
    resized_mask = cv2.resize(mask_img, (width, height), interpolation=cv2.INTER_NEAREST)

    # 保存
    cv2.imwrite(save_path, resized_mask)
    print(f"Mask 已保存到 {save_path}")

if __name__ == '__main__':
    # 示例路径
    rgb_path = r"C:\Users\GHB\Desktop\test_dataset\DSC00200.JPG"
    mask_path = r"C:\Users\GHB\Desktop\test_dataset\Attunet\DSC00200_main_skeleton.jpg"
    save_path = r"C:\Users\GHB\Desktop\test_dataset\Attunet\DSC00200_main_skeleton_resized.jpg"

    resize_mask_to_rgb(mask_path, rgb_path, save_path)
