# BoolSqli
布尔注入工具

# 用法
同sqlmap
```
optional arguments:
  -h, --help            help of the BoolSqli.py program
  --version             show program's version number and exit

Necessary parameter:
  -u url, --url url     *目标url 多个用空格分隔
  -D url                数据库名
  --dbs                 读取数据库
  -T url                表名
  --tables              读取表
  -C [url [url ...]]    列名
  --columns             读取列
  --dump                读取字段
  -o str, --ok_word str
                        正确页面关键词
  -n str, --no_word str
                        错误页面关键词

other arguments:
  --level level         程序运行级别:CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET
  --delay num           访问延迟
  --cookie str          cookie
```
