import requests


class LoginDouban:
    """
    豆瓣站点登录
    - 无验证码，密码明文提交
    """
    # 登录操作会话对象
    session = requests.session()
    common_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}

    def __init__(self, username: str, password: str, **kwargs):
        self.username = username
        self.password = password
        # 豆瓣主页url
        self.home_url = 'https://www.douban.com/'
        # 账号密码提交url
        self.submit_url = 'https://accounts.douban.com/j/mobile/login/basic'
        self._init_session()
        # 设置是否登录成功标志
        self.login_success = False
        # 个人信息
        self.user_info = None

    def login(self):
        """执行登录操作
        :return: `rtype:dict` 登录结果
        """
        login_status_info = {'code': 1, 'state': 'failed', 'message': ''}
        submit_form_data = {
            'ck': '',
            'name': self.username,
            'password': self.password,
            'remember': 'false',
            'ticket': ''
        }
        login_headers = self.common_headers.copy()
        login_headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://accounts.douban.com',
            'Referer': 'https://accounts.douban.com/passport/login_popup?login_source=anony',
            'X-Requested-With': 'XMLHttpRequest'})
        login_resp = self.session.post(url=self.submit_url, data=submit_form_data, headers=login_headers)
        if login_resp.status_code == 200:
            login_json = login_resp.json()
            if login_json.get('status') == 'success':
                login_status_info['code'] = 0
                login_status_info['state'] = 'success'
                login_status_info['message'] = '登陆成功, %s' % login_json.get('description')
                self.login_success = True
                self.user_info = login_json.get('payload', {}).get('account_info')
            elif login_json.get('status') == 'failed':
                login_status_info['message'] = '登录失败, %s' % login_json.get('description')
            else:
                login_status_info['message'] = '未知原因, %s' % login_resp.text
        else:
            login_status_info['message'] = '提交登录信息失败'
        return login_status_info

    def get_user_info(self):
        """获取用户信息
        :return: 登录成功`rtype:dict`, 登录失败`rtype:None`
        """
        if self.login_success and isinstance(self.user_info, dict):
            return {
                'username': self.user_info.get('name'),
                'user_id': self.user_info.get('id'),
                'avatar': self.user_info.get('avatar', {}).get('large')
            }
        else:
            return None

    def get_login_cookies(self) -> dict:
        """获取用户登录后的cookies"""
        return requests.utils.dict_from_cookiejar(self.session.cookies)

    def _init_session(self):
        """初始化会话对象"""
        try:
            self.session.get(url=self.home_url, headers=self.common_headers)
        except requests.exceptions.RequestException:
            pass


if __name__ == '__main__':
    test_name = 'your username'
    test_password = 'your password'
    login_obj = LoginDouban(username=test_name, password=test_password)
    # 开始执行登录操作
    login_result = login_obj.login()
    print('登录结果>>', login_result)
    # 获取用户信息
    user_info = login_obj.get_user_info()
    print('用户信息>>', user_info)
    # 获取登录状态cookies
    cookies = login_obj.get_login_cookies()
    print('Cookies>>', cookies)
