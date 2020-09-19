# -*- coding: utf-8 -*- 
# @Author : Leo

import requests

from lxml import etree


class LoginWebsiteName:
    """登录程序结构"""
    # 登录操作会话对象
    session = requests.session()
    common_headers = {
        'Host': 'github.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}

    def __init__(self, username: str, password: str, **kwargs):
        self.username = username
        self.password = password
        # 登录页面
        self.login_page_url = 'https://github.com/login'
        # 登录信息提交api
        self.submit_url = 'https://github.com/session'
        # 用户信息
        self.user_info = None

    def login(self) -> dict:
        """执行登录操作
        :return: `rtype:dict` 登录结果
        """
        login_status_info = {'code': 1, 'state': 'failed', 'message': ''}
        authenticity_token = self._get_authenticity_token()
        if authenticity_token is None:
            raise ValueError('extract `authenticity_token` failed!')
        # print(authenticity_token)
        login_form_data = {
            'commit': 'Sign in',
            'utf8': '✓',
            'authenticity_token': authenticity_token,
            'login': self.username,
            'password': self.password,
            'webauthn-support': 'supported'}
        resp = self.session.post(url=self.submit_url, data=login_form_data, headers=self.common_headers, timeout=5)
        # 验证是否登录成功
        if resp.status_code in (200, 302):
            logged_page_doc = etree.HTML(resp.text)
            logged_username = logged_page_doc.xpath('//head/meta[@name="octolytics-actor-login"]/@content')
            if logged_username:
                login_status_info['code'] = 0
                login_status_info['state'] = 'success'
                login_status_info['message'] = '登录成功，登录用户为 %s' % logged_username[0]
                self._set_user_info(lxml_doc=logged_page_doc)
            else:
                container_tag = logged_page_doc.xpath('//div[@id="js-flash-container"]//div[@class="container"]/text()')
                error_msg = ','.join([con.strip() for con in container_tag if con.strip()])
                login_status_info['message'] = '登录失败，失败原因：%s' % error_msg
        else:
            login_status_info['message'] = '登录失败，提交登录信息响应状态码异常 %d' % resp.status_code
        return login_status_info

    def get_user_info(self) -> dict or None:
        """获取用户信息
        :return: 登录成功`rtype:dict`, 登录失败`rtype:None`
        """
        return self.user_info

    def get_login_cookies(self) -> dict:
        """获取用户登录后的cookies
        :return:
        """
        return requests.utils.dict_from_cookiejar(self.session.cookies)

    def _get_authenticity_token(self):
        """获取authenticity_token"""
        resp = self.session.get(url=self.login_page_url, headers=self.common_headers, timeout=10)
        if resp.status_code == 200:
            login_doc = etree.HTML(resp.text)
            token_tag = login_doc.xpath('//form[@action="/session"]/input[@name="authenticity_token"]/@value')
            return token_tag[0] if token_tag else None
        return None

    def _set_user_info(self, lxml_doc):
        """设置用户信息"""
        self.user_info = dict()
        # 获取用户ID
        userid_tag = lxml_doc.xpath('//head/meta[@name="octolytics-actor-id"]/@content')
        if userid_tag:
            self.user_info['user_id'] = userid_tag[0]
        # 获取用户名
        username_tag = lxml_doc.xpath('//head/meta[@name="octolytics-actor-login"]/@content')
        if username_tag:
            self.user_info['username'] = username_tag[0]
        # 获取头像
        avatar_tag = lxml_doc.xpath('//head/meta[@property="og:image"]/@content')
        if avatar_tag:
            self.user_info['avatar'] = avatar_tag[0]


if __name__ == '__main__':
    test_name = 'your username'
    test_password = 'your password'
    login_obj = LoginWebsiteName(username=test_name, password=test_password)
    # 开始执行登录操作
    login_result = login_obj.login()
    print('登录结果> ', login_result)
    # 获取用户信息
    user_info = login_obj.get_user_info()
    print('用户信息> ', user_info)
    # 获取登录状态cookies
    cookies = login_obj.get_login_cookies()
    print('登录cookies> ', cookies)
