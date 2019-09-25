import requests


class LoginWebsiteName:
    """登录程序结构"""
    # 登录操作会话对象
    session = requests.session()

    def __init__(self, username: str, password: str, **kwargs):
        self.username = username
        self.password = password
        pass

    def login(self) -> dict:
        """执行登录操作
        :return: `rtype:dict` 登录结果
        """
        pass

    def get_user_info(self) -> dict or None:
        """获取用户信息
        :return: 登录成功`rtype:dict`, 登录失败`rtype:None`
        """
        pass

    def get_login_cookies(self) -> dict:
        """获取用户登录后的cookies
        :return:
        """
        pass


if __name__ == '__main__':
    test_name = 'your username'
    test_password = 'your password'
    login_obj = LoginWebsiteName(username=test_name, password=test_password)
    # 开始执行登录操作
    login_result = login_obj.login()
    # 获取用户信息
    user_info = login_obj.get_user_info()
    # 获取登录状态cookies
    cookies = login_obj.get_login_cookies()
