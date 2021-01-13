# JNU-Heatlth-Checkin
## 介绍
基于Github Action完成自动化的每日健康打卡工作。

## 触发方式
* 点亮`Star`
* 凌晨1点4分和早上8点4分定时执行
* 自定义：编辑`.github/workflows/auto-checkin.yml`

## 使用方式
* 点击右上角 Fork 项目
* Settings *> Secrets 中添加账号、SCKEY：
  - `USERNAME`：账号
  - `PASSWORD`：密码
  - `SCKEY`：Server酱SCKEY，用于微信推送结果。(可选)
* 点击`Star`，任务会自动执行，运行进度和结果可以在Actions页面查看
* 当任务运行完成时，会将运行结果打包到Artifacts，可自行下载查看
* 如果配置了Server酱，运行结果会推送到微信

## 获取Server酱SCKEY
* github 授权登录[Server酱](http://sc.ftqq.com/3.version)官网
* 菜单栏[微信推送](http://sc.ftqq.com/?c=wechat&a=bind)扫描绑定微信
* 菜单栏[发送消息](http://sc.ftqq.com/?c=code)拷贝SCKEY
