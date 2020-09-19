# -*- coding: utf-8 -*- 
# @Author : Leo

import time
from hashlib import md5

import requests


class LoginZGC:
    """中关村在线站点登录"""
    # 登录操作会话对象
    session = requests.session()

    def __init__(self, username: str, password: str, **kwargs):
        self.username = username
        self.password = password
        # 主页url
        self.home_url = 'http://www.zol.com.cn/'
        # 登录信息提交url
        self.submit_login_url = 'http://service.zol.com.cn/user/ajax/login2014/login.php'
        # ip_ck获取url
        self.ipck_url = 'http://js.zol.com.cn/pvn/pv.ht?&t={t}&c={c}'
        # headers
        self.base_headers = {
            'Origin': 'http://service.zol.com.cn',
            'Referer': 'http://service.zol.com.cn/user/login.php?backUrl=http://www.zol.com.cn/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'}
        self.login_flag = False

    def login(self) -> dict:
        """执行登录操作
        :return: `rtype:dict` 登录结果
        """
        login_status = {'code': 1, 'state': 'failed', 'message': ''}
        # 提交账号密码form-data
        submit_form = {
            'userid': self.username,
            'pwd': self._get_password_md5(),
            'is_auto': 1,
            'backUrl': 'http://www.zol.com.cn/'
        }
        submit_headers = self.base_headers.copy()
        submit_headers['Content-type'] = 'application/x-www-form-urlencoded'
        # 如果不携带cookies，及时账号密码正确响应数据也会为{"info": "error", "msg": "账号或密码错误,请重试", "ext": "errMsg"}
        ip_ck = self._get_ipck()
        if ip_ck is None:
            raise ValueError('获取ip_ck失败')
        init_cookies = {'ip_ck': ip_ck}
        login_resp = self.session.post(url=self.submit_login_url, data=submit_form, cookies=init_cookies)
        if login_resp.status_code == 200:
            resp_data = login_resp.json()
            if isinstance(resp_data, dict) and resp_data.get('info') == 'ok':
                self.login_flag = True
                login_status['code'] = 0
                login_status['state'] = 'success'
                login_status['message'] = '登陆成功'
            else:
                login_status['message'] = '登录失败，响应信息: %s' % resp_data.get('msg')
        else:
            login_status['message'] = '提交登录信息时响应状态码非200'
        return login_status

    def get_user_info(self) -> dict or None:
        """获取用户信息
        :return: 登录成功`rtype:dict`, 登录失败`rtype:None`
        """
        return {} if self.login_flag else None

    def get_login_cookies(self) -> dict:
        """获取用户登录后的cookies
        :return:
        """
        return requests.utils.dict_from_cookiejar(self.session.cookies)

    def _get_password_md5(self):
        """获取提交时进行md5摘要的密码字段
        hiddenPwd = CryptoJS.MD5(password + "zol");
        """
        return md5((self.password + 'zol').encode(encoding='UTF-8')).hexdigest()

    def _get_ipck(self):
        """获取cookies中的ip_ck，经测试该字段为提交登录时的必需字段"""
        pv_resp = self.session.get(url=self.ipck_url.format(t=int(time.time() / 1000), c=''))
        if pv_resp.status_code == 200:
            return pv_resp.json().get('ipck')
        return None


if __name__ == '__main__':
    import json

    test_name = 'your username'
    test_password = 'your password'
    login_obj = LoginZGC(username=test_name, password=test_password)
    # 开始执行登录操作
    login_result = login_obj.login()
    print('登录结果>>', json.dumps(login_result, ensure_ascii=False))
    # 获取用户信息
    user_info = login_obj.get_user_info()
    print('TODO 没有必要的用户信息可获取 >>', json.dumps(user_info, ensure_ascii=False))
    # 获取登录状态cookies
    cookies = login_obj.get_login_cookies()
    print('会话cookies >>', json.dumps(cookies, ensure_ascii=False))
