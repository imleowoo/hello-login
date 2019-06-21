# -*- coding: utf-8 -*-
# @Author : Leo


import os
import requests


class LoginIFeng:
    """
    登陆凤凰新闻站点脚本
    - PC浏览器页面实现
    - 登录需要验证码
    - 其中密码以明文提交
    """
    # 会话对象
    session = requests.session()
    session.headers.update({
        'Host': 'id.ifeng.com',
        'Origin': 'https://id.ifeng.com',
        'Referer': 'https://id.ifeng.com/user/login',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    })

    def __init__(self, username: str, password: str, **kwargs):
        self.username = username
        self.password = password
        # 登陆页面url
        self.login_page_url = 'https://id.ifeng.com/user/login'
        # 登陆信息提交链接
        self.login_submit_url = 'https://id.ifeng.com/api/login'
        # 验证码请求地址
        self.captcha_url = 'https://id.ifeng.com/public/authcode'

        # 登陆提交form-data
        # u: 账号 k:明文密码 auth:验证码
        self.form_data = {
            'u': '',
            'k': '',
            'auth': '',
            'type': '3',
            'comfrom': ''}
        self.login_success_flag = False
        # 存储登录之后的响应信息
        self.resp_data = None

    def login(self):
        """
        执行登录操作
        :return: `rtype:dict` 登录结果
        """
        login_status_info = {'code': 1, 'state': 'failed', 'message': ''}
        self.session.get(url=self.login_page_url)
        code_text = self._get_code_image()
        if code_text is None:
            login_status_info['message'] = '未获取到验证码'
        else:
            self.session.headers.update({
                'Upgrade-Insecure-Requests': '1',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Referer': 'http://id.ifeng.com/allsite/login'
            })
            self._set_form_data(captcha_text=code_text)
            login_resp = self.session.post(url=self.login_submit_url, data=self.form_data)
            if login_resp.status_code == 200:
                resp_json = login_resp.json()
                if resp_json.get('code') == 1 and 'data' in resp_json:
                    self.login_success_flag = True
                    self.resp_data = resp_json.get('data')
                    login_status_info['code'] = 0
                    login_status_info['state'] = 'success'
                    login_status_info['message'] = '登录成功'
                # 登录错误时
                elif resp_json.get('code') == 0:
                    login_status_info['message'] = resp_json.get('message')
                # 登录出现未知原因
                else:
                    login_status_info['message'] = '未知原因: %s' % login_resp.text
        return login_status_info

    def get_user_info(self):
        """获取用户信息"""
        if self.login_success_flag and self.resp_data is not None:
            return {'username': self.resp_data.get('nickname', ''),
                    'profile': self.resp_data.get('url', '')}
        return None

    def get_login_cookies(self):
        """获取用户登录后的cookies"""
        return requests.utils.dict_from_cookiejar(self.session.cookies)

    def _get_code_image(self):
        """获取验证码图片内容"""
        captcha_resp = self.session.get(url=self.captcha_url)
        if captcha_resp.status_code == 200:
            open('captcha_image.jpg', 'wb').write(captcha_resp.content)
            code_text = input('输入本次请求的验证码>>')
            os.remove('captcha_image.jpg')
            return code_text
        return None

    def _set_form_data(self, captcha_text):
        """设置登陆时提交的form-data"""
        self.form_data['u'] = self.username
        self.form_data['k'] = self.password
        self.form_data['auth'] = captcha_text


if __name__ == '__main__':
    test_name = 'your username'
    test_password = 'your password'
    login_obj = LoginIFeng(username=test_name, password=test_password)
    # 开始执行登录操作
    login_result = login_obj.login()
    print(login_result)
    # 获取用户信息
    user_info = login_obj.get_user_info()
    print(user_info)
    # 获取登录状态cookies
    cookies = login_obj.get_login_cookies()
    print(cookies)
