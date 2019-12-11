import argparse

# admin指令解析器
parser = argparse.ArgumentParser(
    prog='admin',  # 解析的是哪个指令
    usage='%(prog)s [options]',  # 用法说明 会显示在help里
    description='管理员指令',  # 指令描述 会显示在help里
    epilog="用这些指令管理成员的权限",  # help显示完，最后的文案
    add_help=False  # 是否添加默认的-h 和--help指令显示内容
)

parser.add_argument('--test', help='test of the %(prog)s program')
parser.add_argument('--foo',  # 有前缀'-'或'--' 代表是flag参数
                    nargs='?',  # 单一参数允许的参数数量 ？是未知
                    const='c',  # 只填写--foo 后面不跟随东西默认为const
                    default='d')  # 在没有后缀--foo时取default值
parser.add_argument('bar', nargs='+',  # 如果没有则会报错
                    help='bar help'  # 帮助说明
                    )
parser.add_argument('door',  # 没有前缀'-' 代表是位置参数
                    type=int,  # 参数的类型
                    choices=range(1, 4),  # 值的可选范围
                    required=True,  # 是否必填
                    metavar='XXX',  # 位置参数的name不应该被看到，应该用metavar说明
                    dest='bar' # 这个参数本身不生成arg中的字段，而是将内容给bar
                    )

parser.add_argument('--version', '-v', action='version', version='%(prog)s 1.0 你TM是程序员吧，看这东西')

sub_parser = argparse.ArgumentParser(
    parents=[parser],  # 继承parser的父指令相关参数信息
    formatter_class=argparse.RawDescriptionHelpFormatter  # 指定帮助文档的格式类
)

sub_parser.print_help()

arg = sub_parser.parse_args(['bar', 'YYY'])
print(arg)
