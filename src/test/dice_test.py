import unittest
import dice
import user_gen


class DiceTest(unittest.TestCase):
    test_content = {}

    @classmethod
    def setUpClass(self):
        # 必须使用@classmethod 装饰器,所有test运行前运行一次
        print('测试开始\n')
        self.test_content['sender'] = {'user_id': 123456789, 'nickname': '桃毒专用测试'}
        self.test_content['message'] = '.gen 天子'
        result = user_gen.gen(self.test_content)
        print(result)


    @classmethod
    def tearDownClass(self):
        # 必须使用 @ classmethod装饰器, 所有test运行完后运行一次
        self.test_content['message'] = '.drop 天子'
        result = user_gen.drop(self.test_content)
        print(result)
        test_content = {}
        print('测试结束')


    def setUp(self):
        # 每个测试用例执行之前做操作
        self.test_content['message']=''

    def tearDown(self):
        # 每个测试用例执行之后做操作
        self.test_content['message'] = ''

    def test_dice_ex(self):
        self.test_content['message'] = '.r4#d20+8-2d6'
        result = dice.dice_ex(self.test_content)
        print(result)

    def test_jrrp(self):
        result = dice.jrrp(self.test_content)
        print(result)

    def test_check(self):
        self.test_content['message'] = '.check 力量豁免'
        result = dice.check(self.test_content)
        print(result)

    def test_dnd(self):
        result = dice.random_attribute(self.test_content)
        print(result)


if __name__ == '__main__':
    unittest.main()  # 运行所有的测试用例
