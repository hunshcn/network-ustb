# 上网登录程序

## 食用方法
自行编译吧，因为用户名密码是硬编码在代码里的，外部输入我个人也不太喜欢

能够解决偶尔网页登录不上去账号的奇怪问题

如果用于路由器，可能需要选择合适架构，一般是mips并且去掉浮点

`GOOS=linux;GOARCH=mipsle;CGO_ENABLED=0;GOMIPS=softfloat`