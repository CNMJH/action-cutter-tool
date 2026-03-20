@echo off
title 游戏动作裁剪工具一键打包
echo ==============================================
echo 正在安装依赖（仅第一次运行需要）...
echo ==============================================
pip install pysimplegui pyinstaller -i https://pypi.tuna.tsinghua.edu.cn/simple
echo.
echo ==============================================
echo 正在打包成独立exe文件...
echo ==============================================
pyinstaller -F -w --add-binary "ffmpeg.exe;." 动作裁剪工具_GUI.py
echo.
echo ==============================================
echo 打包完成！exe文件已生成到dist文件夹内
echo 直接双击dist目录下的「动作裁剪工具_GUI.exe」即可使用
echo ==============================================
pause
