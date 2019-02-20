import unittest
from filter import filter

test_content = {}
sender = {'user_id': 123456789, 'nickname': '桃毒专用测试'}
test_content['sender'] = {'user_id': 123456789, 'nickname': '桃毒专用测试'}

class SpellTest(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        # 必须使用@classmethod 装饰器,所有test运行前运行一次
        print('测试开始\n')
        test_content['message'] = '.gen 天子'
        filter(test_content)
        test_content['message'] = ''

    @classmethod
    def tearDownClass(self):
        # 必须使用 @ classmethod装饰器, 所有test运行完后运行一次
        test_content = {}
        test_content['message'] = '.drop 天子'
        test_content['sender'] = sender
        filter(test_content)
        test_content['message'] = ''
        print('测试结束')

    def setUp(self):
        # 每个测试用例执行之前做操作
        test_content['message'] = ''

    def tearDown(self):
        # 每个测试用例执行之后做操作
        test_content['message'] = ''

    def test_dice_ex(self):
        test_content['message'] = '.spell 圣'
        filter(test_content)




if __name__ == '__main__':
    unittest.main()  # 运行所有的测试用例
