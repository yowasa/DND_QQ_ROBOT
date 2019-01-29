import unittest
import user_gen
import attribute_controller

class UserTest(unittest.TestCase):
    test_content = {}

    @classmethod
    def setUpClass(self):
        # 必须使用@classmethod 装饰器,所有test运行前运行一次
        print('测试开始\n')
        self.test_content['sender'] = {'user_id': 123456789, 'nickname': '桃毒专用测试'}
        self.test_content['message'] = '.gen 天子'
        result = user_gen.gen(self.test_content)
        self.test_content['message'] = '.gen 天天子'
        result = user_gen.gen(self.test_content)
        print(result)

    @classmethod
    def tearDownClass(self):
        # 必须使用 @ classmethod装饰器, 所有test运行完后运行一次
        self.test_content['message'] = '.drop 天子'
        result = user_gen.drop(self.test_content)
        print(result)
        self.test_content['message'] = '.drop 天天子'
        result = user_gen.drop(self.test_content)
        print(result)
        test_content = {}
        print('测试结束')

    def setUp(self):
        # 每个测试用例执行之前做操作
        self.test_content['message'] = ''

    def tearDown(self):
        # 每个测试用例执行之后做操作
        self.test_content['message'] = ''

    # 测试查看属性
    def test_ul(self):
        result = attribute_controller.get_user_list(self.test_content)
        print(result)

    # 测试种族
    def test_switch(self):
        self.test_content['message'] = '.switch 天子'
        result = attribute_controller.switch_user(self.test_content)
        print(result)






if __name__ == '__main__':
    unittest.main()  # 运行所有的测试用例
