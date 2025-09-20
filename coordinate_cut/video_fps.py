import cv2
import os

def video_to_frames(video_path, save_dir):
    """
    将视频分解为图像帧并保存

    :param video_path: 视频文件路径
    :param save_dir: 输出帧图像保存目录
    """
    # 创建保存目录
    os.makedirs(save_dir, exist_ok=True)

    # 打开视频
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("无法打开视频文件")
        return

    frame_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 构造保存路径
        frame_filename = os.path.join(save_dir, f"frame_{frame_idx:05d}.jpg")
        cv2.imwrite(frame_filename, frame)
        print(f"保存帧: {frame_filename}")

        frame_idx += 1

    cap.release()
    print(f"视频分帧完成，总帧数: {frame_idx}")

if __name__ == "__main__":
    video_path = r"C:\Users\GHB\Desktop\video1.mp4"
    save_dir = r"C:\Users\GHB\Desktop\test_video_frames"

    video_to_frames(video_path, save_dir)
