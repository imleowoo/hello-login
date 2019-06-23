# -*- coding: utf-8 -*-
# @Author : Leo

import os
import rsa
import time
import base64
import requests
import binascii
from urllib.parse import quote


class LoginSinaWeibo:
    """
    新浪微博登陆
    - 用户名和密码均加密后提交，其中密码采用rsa加密
    """
    # 创建session会话
    session = requests.session()

    def __init__(self, username, password):
        self.username = username
        self.password = password
        # ssologin.js版本
        self.ssologin_version = 'v1.4.18'
        # 微博登陆首页地址
        self.login_home_url = 'https://weibo.com/login.php'
        # 预登陆参数获取接口
        self.pre_login_params_url = 'https://login.sina.com.cn/sso/prelogin.php'
        # 提交正式登陆数据的链接
        self.real_login_url = 'https://login.sina.com.cn/sso/login.php?client=ssologin.js({js_version})&_={ts}'.format(
            js_version=self.ssologin_version, ts=int(time.time()))
        # 验证码图片地址
        self.captcha_url = "http://login.sina.com.cn/cgi/pin.php?r={ts}&s=0&p={pcid}"
        self.session.headers.update(
            {"User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0"})
        self._init_session()
        # 设置是否登录成功标志
        self.login_success = False
        # 个人信息
        self.user_info = None

    def login(self):
        """开始登陆"""
        login_status_info = {'code': 1, 'state': 'failed', 'message': ''}
        login_form_data = self._pre_login()
        login_resp = self.session.post(url=self.real_login_url, data=login_form_data)
        login_resp_json = login_resp.json()
        # 登录成功
        if login_resp_json.get('retcode') == '0':
            self.login_success = True
            self.user_info = {'username': login_resp_json.get('uid'), 'nickname': login_resp_json.get('nick')}
            login_status_info['code'] = 0
            login_status_info['state'] = 'success'
            login_status_info['message'] = '登录成功，获取到的用户名: %s' % login_resp_json.get('nick')
        # 验证码不正确
        elif login_resp_json.get('retcode') == '2070':
            login_status_info['message'] = '登录失败，%s' % login_resp_json.get('reason')
        elif login_resp_json.get('retcode') == '101':
            login_status_info['message'] = '登录失败，%s' % login_resp_json.get('reason')
        else:
            login_status_info['message'] = '登录失败，登录返回结果 %s' % login_resp.text
        return login_status_info

    def get_user_info(self):
        """获取用户信息
        :return: 登录成功`rtype:dict`, 登录失败`rtype:None`
        """
        return self.user_info if self.login_success else None

    def get_login_cookies(self) -> dict:
        """获取用户登录后的cookies"""
        return requests.utils.dict_from_cookiejar(self.session.cookies)

    def _init_session(self):
        """初始化请求会话"""
        try:
            self.session.get(url=self.login_home_url)
        except requests.exceptions.RequestException:
            pass

    def _pre_login(self):
        """预登陆操作，获取相关参数"""
        # 获取提交的用户名
        s_username = self._get_su()
        # 获取提交登陆时需要的参数
        json_data = self._get_login_form_data(su=s_username)
        # # 获取提交的密码字符串
        # s_password = self._get_s_password(json_data=json_data)
        s_password = self._get_s_password(server_time=json_data.get('servertime'),
                                          nonce=json_data.get('nonce'),
                                          pubkey=json_data.get('pubkey'))
        # 设置提交登陆操作时
        login_form_data = {
            'entry': 'weibo',
            'gateway': '1',
            'from': '',
            'savestate': '7',
            'userticket': '1',
            'vsnf': '1',
            'service': 'miniblog',
            'encoding': 'UTF-8',
            'pwencode': 'rsa2',
            'sr': '1280*800',
            'prelt': '529',
            'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
            'rsakv': json_data.get('rsakv'),
            'servertime': json_data.get('servertime'),
            'nonce': json_data.get('nonce'),
            'su': s_username,
            'sp': s_password,
            'returntype': 'TEXT'
        }
        # print(json.dumps(login_form_data, ensure_ascii=False))
        # 需要验证码时
        if json_data.get('pcid'):
            current_captcha_url = self.captcha_url.format(ts=int(time.time()), pcid=json_data.get('pcid'))
            captcha_resp = self.session.get(url=current_captcha_url)
            temp_captcha_file = 'weibo_captcha.jpg'
            open(temp_captcha_file, 'wb').write(captcha_resp.content)
            # TODO 2019-06-24 开放验证码识别接口 http://captcha.faceme.site/sina
            # 使用方式见README-IDEAs.md文档
            captcha_text = input('验证码保存路径为 %s\n验证码的值为> ' % os.path.abspath(temp_captcha_file))
            login_form_data['pcid'] = json_data.get('pcid')
            login_form_data['door'] = captcha_text
        return login_form_data

    def _get_su(self):
        """获取真实的执行登陆操作时提交的用户名"""
        # 用户名先进行url编码
        username_quote = quote(self.username)
        # 再经过base64进行编码
        username_base64 = base64.b64encode(username_quote.encode('utf-8'))
        return username_base64.decode('utf-8')

    def _get_s_password(self, server_time, nonce, pubkey):
        """获取将密码加密后用于登录的字符串"""
        encode_password = (str(server_time) + "\t" + str(nonce) + "\n" + str(self.password)).encode("utf-8")
        public_key = rsa.PublicKey(int(pubkey, 16), int('10001', 16))
        encry_password = rsa.encrypt(encode_password, public_key)
        password = binascii.b2a_hex(encry_password)
        return password.decode()

    def _get_login_form_data(self, su):
        """获取登陆form-data提交的参数`servertime`,`nonce`,`pubkey`,`rsakv`,`showpin`,etc"""
        pre_login_params = {
            'entry': 'weibo',
            'rsakt': 'mod',
            'checkpin': '1',
            'client': 'ssologin.js({js_version})'.format(js_version=self.ssologin_version),
            'su': su,
            '_': int(time.time() * 1000)}
        try:
            resp = self.session.get(url=self.pre_login_params_url, params=pre_login_params)
            if resp.status_code == 200 and resp.json().get('retcode') == 0:
                json_data = resp.json()
                return json_data
            else:
                raise ValueError('请求获取的数据无效')
        except (requests.exceptions.RequestException, ValueError):
            raise Exception('获取form-data参数出错')


if __name__ == '__main__':
    test_username = 'your username'
    test_password = 'your password'
    loginer = LoginSinaWeibo(username=test_username, password=test_password)
    # 开始执行登录操作
    login_result = loginer.login()
    print('登录结果：', login_result)
    # 获取用户信息
    user_info = loginer.get_user_info()
    print('用户信息：', user_info)
    # 获取登录状态cookies
    cookies = loginer.get_login_cookies()
    print('登录Cookies：', cookies)
