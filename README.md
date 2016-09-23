# BoolSqli
布尔注入工具

目前:
支持get和post方法
支持中文数据gbk&utf-8

注：
>get  ：要求注入点参数是返回错误页面，or Ture 后为正确页面，且注入点放到最后一个参数
>post ：要求注入点参数是返回错误页面，or Ture 后为正确页面，且注入点用*号标识
具体请看示例

# 用法
同sqlmap

```
usage: BoolSqli.py [options]

        作者：End1ng blog:end1ng.wordpress.com
        --------------------------------
        Boolean-based blind SQL injection

optional arguments:
  -h, --help            help of the BoolSqli.py program
  --version             show program's version number and exit

Necessary parameter:
  -u url, --url url     *目标url 多个用空格分隔
  -p [data [data ...]], --post [data [data ...]]
                        post数据,注入点用*标识 eg:*user=username pass=password
  -D url                数据库名
  --dbs                 读取数据库
  -T url                表名
  --tables              读取表
  -C [url [url ...]]    列名
  --columns             读取列
  --dump                读取字段

other arguments:
  --level level         程序运行级别:CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET
  --delay num           访问延迟
  --cookie str          cookie
```

# 例子：

GET
注入点 id
```
python BoolSqli.py -u"http://xxx/sqli-labs-master/Less-7/?xxx=1&id=-1'))" --dbs
```

POST
注入点 userName
```
python BoolSqli.py -u "http://xxx/login.php" -p "pwd=123" "*userName=1'" --dbs
```

