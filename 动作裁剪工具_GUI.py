import PySimpleGUI as sg
import os
import subprocess
import threading
# 界面配置
sg.theme("LightBlue2")
layout = [
    [sg.Text("游戏动作批量裁剪工具", font=("微软雅黑", 18))],
    [sg.Text("="*60)],
    [sg.Text("1. 选择视频文件夹："), sg.Input(key="folder", size=(40,1)), sg.FolderBrowse("选择文件夹")],
    [sg.Text("2. 选择裁剪模式：")],
    [sg.Radio("全自动模式（自动去空帧+保留1个动作循环，适合3次循环录制）", "mode", default=True, key="auto_mode")],
    [sg.Radio("手动模式（导入自定义裁剪规则）", "mode", key="manual_mode")],
    [sg.Text("3. 裁剪参数调整（仅自动模式生效）：")],
    [sg.Text("空帧检测阈值："), sg.Slider(range=(0,1), default_value=0.1, resolution=0.05, orientation="h", size=(30,15), key="black_thresh")],
    [sg.Text("动作循环个数："), sg.Slider(range=(2,5), default_value=3, orientation="h", size=(30,15), key="loop_count")],
    [sg.Output(size=(70,10), key="output")],
    [sg.Button("开始处理", size=(15,2)), sg.Button("打开输出目录", size=(15,2)), sg.Button("退出", size=(10,2))]
]
window = sg.Window("游戏动作批量裁剪工具 v1.0", layout, font=("微软雅黑", 10))
# 内置FFmpeg路径（打包时会一起打包进去）
FFMPEG_PATH = "ffmpeg.exe" if os.path.exists("ffmpeg.exe") else "ffmpeg"
def process_videos(folder, is_auto, black_thresh, loop_count):
    os.chdir(folder)
    output_dir = "裁剪完成"
    os.makedirs(output_dir, exist_ok=True)
    video_files = [f for f in os.listdir(folder) if f.lower().endswith((".mp4", ".mov", ".avi"))]
    if not video_files:
        print("❌ 所选文件夹里没有找到视频文件")
        return
    print(f"✅ 找到 {len(video_files)} 个视频文件，开始处理...")
    for idx, file in enumerate(video_files, 1):
        print(f"\n▶️  正在处理第 {idx}/{len(video_files)} 个：{file}")
        try:
            if is_auto:
                # 自动裁剪逻辑
                # 1. 检测空帧
                cmd = [FFMPEG_PATH, "-i", file, "-vf", f"blackdetect=d=0.2,blackframe={black_thresh}", "-f", "null", "-"]
                result = subprocess.run(cmd, capture_output=True, text=True)
                black_info = [line for line in result.stderr.split("\n") if "blackdetect" in line]
                start_trim = 0
                end_trim = float(subprocess.check_output([FFMPEG_PATH, "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", file]).decode().strip())
                if black_info:
                    try:
                        start_trim = float([line.split("black_start:")[1].split()[0] for line in black_info][0])
                        end_trim = float([line.split("black_end:")[1].split()[0] for line in black_info][-1])
                    except:
                        pass
                # 2. 裁剪空帧
                temp_file = f"temp_{file}"
                subprocess.run([FFMPEG_PATH, "-i", file, "-ss", str(start_trim), "-to", str(end_trim), "-c", "copy", temp_file, "-y", "-hide_banner", "-loglevel", "error"], check=True)
                # 3. 按循环数裁剪单循环
                duration = float(subprocess.check_output([FFMPEG_PATH, "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", temp_file]).decode().strip())
                single_cycle = duration / loop_count
                cut_start = single_cycle
                # 4. 输出最终文件
                output_path = os.path.join(output_dir, f"{os.path.splitext(file)[0]}_裁剪完成.mp4")
                subprocess.run([FFMPEG_PATH, "-i", temp_file, "-ss", str(cut_start), "-t", str(single_cycle), "-s", "1920x1080", "-r", "30", "-c:v", "libx264", "-crf", "18", "-c:a", "aac", output_path, "-y", "-hide_banner", "-loglevel", "error"], check=True)
                os.remove(temp_file)
                print(f"✅ 处理完成：{output_path}")
            else:
                # 手动模式读取同目录下cut_rules.txt，格式每行：文件名,开始时间,结束时间
                print("❌ 手动模式请在视频文件夹下新建cut_rules.txt，每行格式：文件名,开始秒数,结束秒数")
                return
        except Exception as e:
            print(f"❌ 处理失败 {file}：{str(e)}")
    print(f"\n🎉 全部处理完成！文件保存在 {os.path.join(folder, output_dir)}")
while True:
    event, values = window.read()
    if event in (sg.WINDOW_CLOSED, "退出"):
        break
    if event == "开始处理":
        folder = values["folder"]
        if not folder or not os.path.isdir(folder):
            sg.popup_error("请先选择正确的视频文件夹！")
            continue
        is_auto = values["auto_mode"]
        black_thresh = values["black_thresh"]
        loop_count = values["loop_count"]
        threading.Thread(target=process_videos, args=(folder, is_auto, black_thresh, loop_count), daemon=True).start()
    if event == "打开输出目录":
        folder = values["folder"]
        if folder and os.path.isdir(folder):
            output_dir = os.path.join(folder, "裁剪完成")
            os.startfile(output_dir)
window.close()
