import time
import requests
from hashlib import md5


class LoginSohu:
    """
    搜狐新闻登录
    - 采用移动端浏览器Web页面进行登录
    - 无验证码，密码采用md5加密
    """
    # 会话对象
    session = requests.session()

    def __init__(self, username, password, **kwargs):
        self.username = username
        self.password_md5 = self._get_password_md5(password)
        # 登录页面url
        self.login_page_url = 'https://m.passport.sohu.com/app/login'
        # 登录页面参数
        self.login_page_params = {'appid': 116001, 'r': 'https://m.sohu.com/ucenter?_from=passport'}
        # 帐号信息登录提交地址
        self.submit_login_url = 'https://m.passport.sohu.com/security/login?t=' + str(int(time.time() * 1000))
        # 获取个人信息
        self.user_info_url = 'http://v2.sohu.com/user/info/web'
        # Mobile-headers
        self.mobile_headers = {
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'}
        # PC-headers
        self.pc_headers = {
            'Host': 'www.sohu.com',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
        self._init_session()
        # 设置是否登录成功标志
        self.login_success = False

    def login(self):
        """执行登录操作
        :return: `rtype:dict` 登录结果
        """
        login_status_info = {'code': 1, 'state': 'failed', 'message': ''}
        submit_form_data = {
            'userid': self.username,
            'password': self.password_md5,
            'appid': 116001}
        self.mobile_headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://m.passport.sohu.com',
            'Referer': 'https://m.passport.sohu.com/app/login?appid=116001&r=https%3A%2F%2Fm.sohu.com%2Fucenter%3F_from%3Dpassport'})
        login_resp = self.session.post(url=self.submit_login_url, data=submit_form_data, headers=self.mobile_headers)
        if login_resp.status_code == 200:
            login_json = login_resp.json()
            if isinstance(login_json, dict) and login_json.get('status') == 200 and login_json.get('message') == 'Success':
                login_status_info['code'] = 0
                login_status_info['state'] = 'success'
                login_status_info['message'] = '登录成功'
                self.login_success = True
            else:
                # 帐号密码存在问题
                if isinstance(login_json, dict) and login_json.get('status') in {404, 459}:
                    login_status_info['message'] = '错误信息:%s' % login_json.get('message')
                else:
                    login_status_info['message'] = '登录失败: %s' % login_json
        else:
            login_status_info['message'] = '提交登录信息失败'
        return login_status_info

    def get_user_info(self):
        """获取用户信息"""
        if self.login_success:
            user_resp = self.session.get(url=self.user_info_url, headers=self.pc_headers)
            user_info = user_resp.json()
            return {'username': user_info.get('userName'), 'avatar': user_info.get('avatar')}
        else:
            return None

        pass

    def get_login_cookies(self):
        """获取用户登录后的cookies"""
        return requests.utils.dict_from_cookiejar(self.session.cookies)

    @staticmethod
    def _get_password_md5(password):
        """密码的md5字符串"""
        return md5(password.encode(encoding='UTF-8')).hexdigest()

    def _init_session(self):
        """初始化会话对象"""
        try:
            self.session.get(url=self.login_page_url, params=self.login_page_params, headers=self.mobile_headers)
        except requests.exceptions.RequestException:
            pass


if __name__ == '__main__':
    test_name = 'your username'
    test_password = 'your password'
    login_obj = LoginSohu(username=test_name, password=test_password)
    # 开始执行登录操作
    login_result = login_obj.login()
    print(login_result)
    # 获取用户信息
    user_info = login_obj.get_user_info()
    print(user_info)
    # 获取登录状态cookies
    cookies = login_obj.get_login_cookies()
    print(cookies)
