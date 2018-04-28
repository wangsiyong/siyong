# SigmaLabelTool版本更新流程

**首先, 请先确认电脑已经安装[Slicer 4.8.1(点我下载)](https://download.slicer.org/)**

## 概述
1. 将最新版本的压缩包解压到固定文件夹
2. 将解压出来的文件夹目录添加到`Slicer`的模块中
3. 设置默认启动模块

## 详细步骤

### A. 解压最新版本压缩包到固定文件夹下
   解压最新提供的压缩包`SigmaLabelTool.zip`, 将解压出的文件夹移至固定文件夹下, 这里移至`D:\SigmaGui`下示例.
### B. 添加`Slicer`的模块路径
1. 打开Slicer![](../images/slicer.png), 菜单 - Edit - Application Settings(或使用快捷键`Ctrl + 2`), 如下图, 弹出`Settings`对话框.左侧选择`Modules`.
2. `Remove`(删除)旧版本`SigmaLabelTool`模块路径, 然后`Add`(添加)新版本路径, ==确认修改==  - >重启软件

### C. 设置默认启动模块
在 ==默认启动模块== 有个下拉列表, 点击选择您想要默认加载的模块名, ==确认修改== , 重启软件后生效

![](../images/settings.png)
