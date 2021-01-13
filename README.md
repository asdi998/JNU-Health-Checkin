# JNU-Health-Checkin
## 介绍
基于Github Action完成自动化的每日健康打卡工作。

## 运行方式
* 手动：点亮`Star`
* 自动：凌晨1点和早上8点整定时执行
* 自定义：编辑`.github/workflows/auto-checkin.yml`

## 使用方式
* 点击右上角 Fork 项目
* Settings -> Secrets 中添加账号、SCKEY：
  - `USERNAME`：账号
  - `PASSWORD`：密码
  - `SCKEY`：Server酱SCKEY，用于微信推送结果。(可选)
* 点击`Star`，任务会自动执行，运行进度和结果可以在Actions页面查看
* 如果配置了SCKEY，打卡结果会推送到微信

## 其他说明
* 若当日已经打卡，程序会自动退出，不会重复打卡。
* 程序会自动读取上一次成功打卡的内容，作为这次打卡填写的内容。
* 帐号密码由Github加密存储，任务由Github自动执行，其中的所有隐私信息不会对外泄露。

## 获取Server酱SCKEY
* github 授权登录[Server酱](http://sc.ftqq.com/3.version)官网
* 菜单栏[微信推送](http://sc.ftqq.com/?c=wechat&a=bind)扫描绑定微信
* 菜单栏[发送消息](http://sc.ftqq.com/?c=code)拷贝SCKEY
