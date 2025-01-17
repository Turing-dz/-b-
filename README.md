# 1.js
## 1.1.pip install request pyexecjs
## 1.2.首先根据用户url发送请求，然后对拿到的数据正则化处理，拿到oid（give_oid）
## 1.3.然后根据oid使用js进行请求param的加密，拿到加密后的数据请求评论接口（encode_params，handle_cursor，handle_content，singal_url_comment）
## 1.4.对于有回复的评论，拿到评论的rpid和回复数，翻页请求回复（handle_replay）
#2.qt
## 2.1.pip install PyQt5 pyqt5-tools pyinstaller
## 2.2.python环境\Lib\site-packages\qt5_applications\Qt\bin\ designer.exe(添加动作（edit，添加信号/槽），添加动作函数,保存成ui文件)
## 2.3.python环境\Scripts\ pyuic5.exe(pyuic5.exe  filename -o filename.py)(ui文件转换成py文件)
## 2.4.pyinstaller --onefile --windowed --add-data "comment_url.js;." main_qt.py(打包成exe文件，不要命令框，添加js文件，程序主入口main_qt.py)
