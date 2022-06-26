# 串口读取下位机电阻阵列测量数据

串口通讯协议文档:
https://vjxrg9t6x3.feishu.cn/docs/doccnqQrEd98LYI6Q4244OKlkeh

## 安装Python依赖

```bash
pip3 install -r requirements.txt
```

## 使用


```bash
python3 go.py
```

程序会持续读取串口数据，通过terminal的方式输出实时数据显示，并存储数据文件到当前目录


## 绘制动画

```bash
python viz.py --frames 10
```

默认会找当前目录下 `data_log.txt`，生成 `pressure.mp4`，frames代表要生成动画的帧数。