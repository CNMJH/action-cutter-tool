@echo off
chcp 65001
title 游戏动作批量裁剪工具
echo ==============================================
echo 正在批量处理视频，请稍等...
echo ==============================================
if not exist "处理完成" mkdir "处理完成"
for %%f in (*.mp4 *.mov *.avi) do (
    echo 正在处理：%%f
    :: 裁剪空帧
    ffmpeg.exe -i "%%f" -vf blackdetect=d=0.2 -f null - 2> black_log.txt
    for /f "tokens=2 delims=:" %%a in ('findstr "black_start" black_log.txt ^| head -1') do set start=%%a
    for /f "tokens=3 delims=:" %%a in ('findstr "black_end" black_log.txt ^| tail -1') do set end=%%a
    if not defined start set start=0
    if not defined end set end=%%~zf
    :: 裁剪单循环（3次循环除以3）
    ffmpeg.exe -i "%%f" -ss %start% -to %end% -c copy temp.mp4 -y -hide_banner -loglevel error
    for /f "delims=" %%a in ('ffprobe.exe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 temp.mp4') do set dur=%%a
    set /a single=dur/3
    :: 输出标准1080p30fps
    ffmpeg.exe -i temp.mp4 -ss %single% -t %single% -s 1920x1080 -r 30 -c:v libx264 -crf 18 -c:a aac "处理完成\%%~nf_裁剪完成.mp4" -y -hide_banner -loglevel error
    del temp.mp4 black_log.txt
    echo 完成：%%f
)
echo ==============================================
echo 全部处理完成！文件在「处理完成」文件夹
echo ==============================================
pause
