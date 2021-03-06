import unittest
from filter import filter

test_content = {}
sender = {'user_id': 123456789, 'nickname': '桃毒专用测试'}
test_content['sender'] = {'user_id': 123456789, 'nickname': '桃毒专用测试'}


class CharacterTest(unittest.TestCase):
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


    # 测试创建流程
    def test_gen(self):
        test_content['message'] = '.gen 桃毒'
        filter(test_content)
        test_content['message'] = '.guid'
        filter(test_content)
        test_content['message'] = '.choose 3'
        filter(test_content)
        test_content['message'] = '.guid'
        filter(test_content)
        test_content['message'] = '.drop 桃毒'
        filter(test_content)
        # test_content['message'] = ''
        # filter(test_content)
        # test_content['message'] = ''
        # filter(test_content)
        pass

    # 测试种族
    def test_attr(self):
        pass
        # self.test_content['message'] = '.race 矮人'
        # result = user_gen.switch_race(self.test_content)
        # print(result)
        # result = attribute_controller.watch_attribute(self.test_content)
        # print(result)
        # # 选择亚种
        # self.test_content['message'] = '.subrace 丘陵矮人'
        # result = user_gen.switch_sub_race(self.test_content)
        # print(result)
        # result = attribute_controller.watch_attribute(self.test_content)
        # print(result)

    # 测试重骰
    def test_reroll(self):
        pass
        # result = user_gen.reroll(self.test_content)
        # print(result)

    # 测试交换属性
    def test_swap(self):
        pass
        # self.test_content['message'] = '.swap 力量 敏捷'
        # result = user_gen.swap(self.test_content)
        # print(result)
        # result = attribute_controller.watch_attribute(self.test_content)
        # print(result)

    # 测试自选属性&自选语言
    def test_attr_up(self):
        pass
        # self.test_content['message'] = '.race 半精灵'
        # result = user_gen.switch_race(self.test_content)
        # print(result)
        # result = attribute_controller.watch_attribute(self.test_content)
        # print(result)
        # self.test_content['message'] = '.attrup 力量 敏捷'
        # result = attribute_controller.attr_up(self.test_content)
        # print(result)
        # result = attribute_controller.watch_attribute(self.test_content)
        # print(result)
        # self.test_content['message'] = '.language 龙语'
        # result = attribute_controller.select_language(self.test_content)
        # print(result)
        # result = attribute_controller.watch_attribute(self.test_content)
        # print(result)


if __name__ == '__main__':
    unittest.main()  # 运行所有的测试用例
