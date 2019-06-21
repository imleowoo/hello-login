# -*- coding: utf-8 -*-
# @Author : Leo

import requests
from urllib.parse import urlparse, parse_qs


class LoginToutiao:
    """
    今日头条登陆
    - 头条账号登陆存在验证码
      - PC-Web页面为滑动验证码
      - 移动端页面为图片字母数字验证码
    - 实现：先经过移动端页面进行登录后，再切换至PC页面
    """
    session = requests.session()

    def __init__(self, username, password):
        self.username = username
        self.password = password
        # Mobile 头条首页链接
        self.mobile_home_url = 'https://m.toutiao.com/'
        # 登录页面
        self.login_home_url = 'https://sso.toutiao.com/'
        # 提交用户信息链接
        self.submit_data_url = 'https://sso.toutiao.com/account_login/'
        # session_id 获取地址
        self.session_id_url = 'https://www.toutiao.com/api/pc/login_success/?next=https%3A%2F%2Fwww.toutiao.com%2F&ticket={ticket}'
        # 移动端headers
        self.mobile_headers = {
            'Host': 'sso.toutiao.com',
            'Origin': 'https://sso.toutiao.com',
            'Referer': 'https://m.toutiao.com/',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1'}
        # 登录提交的数据
        self.post_form_data = {'account': self.username,
                               'password': self.password,
                               'captcha': '',
                               'is_30_days_no_login': 'true',
                               'service': 'https://www.toutiao.com/'}
        # 当前验证码识别次数累计
        self.cur_captcha_retry = 0
        # 验证码识别错误尝试次数
        self.max_captcha_retry = 3
        try:
            self.session.get(url=self.mobile_home_url, headers=self.mobile_headers)
        except requests.exceptions.RequestException:
            pass
        # 设置是否登录成功标志
        self.login_success = False
        # 用户ID
        self.user_id = None
        # ticket
        self.ticket = None

    def login(self):
        """开始登陆"""
        login_status_info = {'code': 1, 'state': 'failed', 'message': ''}
        login_resp = self.session.post(url=self.submit_data_url, data=self.post_form_data, headers=self.mobile_headers)
        if login_resp.status_code == 200:
            login_json = login_resp.json()
            # 登陆成功
            if login_json.get('error_code') == 0:
                login_status_info['code'] = 0
                login_status_info['state'] = 'success'
                self.user_id = login_json.get('user_id')
                login_status_info['message'] = '登录成功，获取到的用户ID: %s' % self.user_id
                self.login_success = True
                # 新增其它cookies信息的获取方式
                # 将token加入cookies，发文时会用到
                params_dict = parse_qs(urlparse(login_json.get('redirect_url')).query)
                self.ticket = params_dict.get('ticket')[0] if params_dict.get('ticket') else None
            # 需要输入验证码
            elif login_json.get('error_code') in {1101, 1102} and login_json.get(
                    'captcha') and self.cur_captcha_retry < self.max_captcha_retry:
                # 验证码识别次数加1
                self.cur_captcha_retry += 1
                # 将进行base64编码的验证码图片，识别其中的验证码值
                self.post_form_data['captcha'] = self._get_captcha_value(captcha_base64=login_json.get('captcha'))
                return self.login()
            # 账号密码错误,1033为多次提交错误
            elif login_json.get('error_code') in {1009, 1003}:
                login_status_info['message'] = '账号或密码错误,desc:%s' % login_json.get('description')
            else:
                login_status_info['message'] = '因为其它原因登录失败, %s' % login_resp.text
        else:
            login_status_info['message'] = '提交登录信息失败'
        return login_status_info

    def get_user_info(self):
        """获取用户信息"""
        return {'user_id': self.user_id} if self.login_success else None

    def get_login_cookies(self):
        """
        获取登录cookies
        :return:
        """
        # 如果ticket为非空，则建议更新cookies
        if self.ticket is not None:
            self.session.get(url=self.session_id_url.format(ticket=self.ticket), timeout=3)
        return requests.utils.dict_from_cookiejar(self.session.cookies)

    @staticmethod
    def _get_captcha_value(captcha_base64):
        """
        获取验证码的值
        - 这个方法可以修改为接入验证码识别接口或模型，以获取验证码图片的值
        :param captcha_base64: 进行base64加密的验证码字符串
        :return:
        """
        captcha_data = 'data:image/gif;base64,' + captcha_base64
        print('当前base64编码后的验证码图片: %s' % captcha_data)
        # 可以将该地址复制至浏览器地址栏直接打开
        captcha_str = input('输入验证码:')
        return captcha_str


if __name__ == '__main__':
    test_name = 'your username'
    test_password = 'your password'
    loginer = LoginToutiao(username=test_name, password=test_password)
    login_result = loginer.login()
    print(login_result)
    user_info = loginer.get_user_info()
    print(user_info)
    login_cookies = loginer.get_login_cookies()
    print(login_cookies)
