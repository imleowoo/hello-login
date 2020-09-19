import time
from copy import deepcopy
from hashlib import md5, sha1

import requests


class LoginITouchTV:
    """
    触电新闻后台登录 - https://media.itouchtv.cn/
    - 提交信息时账号密码明文提交，无验证码
    - 登录后进行相关请求时需要生成sign，并且GET和POST请求时加密方式不一致
    """
    # 登录操作会话对象
    session = requests.session()

    def __init__(self, username: str, password: str, **kwargs):
        self.username = username
        self.password = password
        # 登录预检接口和数据提交接口
        self.login_url = 'https://mngapi.itouchtv.cn/v1/signin'
        # 获取详细用户信息接口
        self.user_info_url = 'https://mngapi.itouchtv.cn/v1/media/{media_id}'
        self.common_headers = {
            'Referer': 'https://media.itouchtv.cn/login',
            'User-Agent': 'Mozilla/5.input (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.input.3626.119 Safari/537.36'}
        # get请求时明文字符串
        self.get_method_clear_text_format = '{token}{user_id}{timestamp_ms}'
        # 设置是否登录成功标志
        self.login_success = False
        # 用户的其它标志信息
        self.user_id = None
        self.unique_id = None
        self.media_id = None
        self.token = None
        # 登录状态下获取的用户信息
        self.user_info = None

    def login(self) -> dict:
        """执行登录操作
        :return: 登录结果
        """
        login_status_info = {'code': 1, 'state': 'failed', 'message': ''}
        pre_login_flag = self._pre_login_options()
        # 如果预检请求成功,则开始进行登录
        if pre_login_flag:
            login_headers = deepcopy(self.common_headers)
            login_headers.update({'timestamp': str(int(time.time() * 1000))})
            login_form = {'account': self.username, 'password': self.password, 'remember': True}
            login_resp = self.session.post(url=self.login_url, data=login_form, headers=login_headers)
            if login_resp.status_code == 200:
                # 获取登录响应信息
                login_info = login_resp.json()
                if login_info.get('status') == 200 and login_info.get('code') == 0 and login_info.get(
                        'message') == 'success':
                    self.token = login_info.get('data', {}).get('token')
                    login_status_info['code'] = 0
                    login_status_info['state'] = 'success'
                    login_status_info['message'] = '登录成功,本次登录生成token: %s' % self.token
                    self.login_success = True
                    self._set_user_ids(login_info)
                elif login_info.get('status') == 400:
                    login_status_info['message'] = '登录失败，response_code: %s, response_message: %s' % (
                    login_info.get('code'),
                    login_info.get('message'))
                else:
                    login_status_info['message'] = f'登录失败,原因未知: %s' % login_info
            else:
                login_status_info['message'] = '提交登录信息响应状态码异常'
            return login_status_info

    def get_user_info(self) -> dict or None:
        """获取用户信息
        :return: 登录成功`rtype:dict`, 登录失败`rtype:None`
        """
        if all([self.login_success, self.token, self.user_id, self.unique_id, self.media_id]):
            info_url = self.user_info_url.format(media_id=self.media_id)
            timestamp_ms = int(time.time() * 1000)
            info_headers = deepcopy(self.common_headers)
            info_headers.update(
                {'timestamp': str(timestamp_ms),
                 'uniqueId': self.unique_id,
                 'userId': str(self.user_id),
                 'mediaId': str(self.media_id),
                 'sign': self._get_sign(timestamp_ms)})
            resp = self.session.get(url=info_url, headers=info_headers)
            if resp.status_code == 200:
                resp_info = resp.json()
                if resp_info.get('status') == 200 and resp_info.get('code') == 0:
                    self.user_info = resp_info.get('data')
                else:
                    print('获取用户信息失败, 详细信息：%s' % resp.text)
        else:
            print(
                '获取用户信息条件不完整，缺失参数: %s' % [self.login_success, self.token, self.user_id, self.unique_id, self.media_id])
        return self.user_info

    def get_login_cookies(self) -> dict:
        """获取用户登录后的cookies"""
        return requests.utils.dict_from_cookiejar(self.session.cookies)

    def _pre_login_options(self):
        """关于登录的预检请求"""
        pre_login_headers = deepcopy(self.common_headers)
        pre_login_headers.update({'Access-Control-Request-Method': 'POST',
                                  'Access-Control-Request-Headers': 'mediaid,sign,timestamp,uniqueid,userid'})
        resp = self.session.options(url=self.login_url, headers=pre_login_headers)
        return True if resp.status_code == 200 else False

    def _set_user_ids(self, login_info: dict):
        """
        登录成功后获取用户的userId, uniqueId, mediaId, token
        :return:
        """
        self.user_id = login_info.get('data', {}).get('user', {}).get('id')
        self.unique_id = login_info.get('data', {}).get('user', {}).get('uniqueId')
        media_list = login_info.get('data', {}).get('user', {}).get('media')
        if media_list and isinstance(media_list, list):
            self.media_id = media_list[0].get('id')
        print('userId: {user_id}, uniqueId: {unique_id}, mediaId: {media_id}'.format(user_id=self.user_id,
                                                                                     unique_id=self.unique_id,
                                                                                     media_id=self.media_id))

    def _get_sign(self, timestamp_ms):
        """
        获取GET请求时生成的sign
        :param timestamp_ms: 毫秒时间戳
        :return:
        """
        clear_text = self.get_method_clear_text_format.format(token=self.token, user_id=self.user_id,
                                                              timestamp_ms=timestamp_ms)
        md5_text = md5(clear_text.encode(encoding='UTF-8')).hexdigest()
        sha1_text = sha1(md5_text.encode('utf-8')).hexdigest()
        return sha1_text


if __name__ == '__main__':
    test_name = 'your username'
    test_password = 'your password'
    login_obj = LoginITouchTV(username=test_name, password=test_password)
    # 开始执行登录操作
    login_result = login_obj.login()
    print('登录结果>>', login_result)
    # 获取用户信息
    user_info = login_obj.get_user_info()
    print('用户信息>>', user_info)
    # 获取登录状态cookies
    cookies = login_obj.get_login_cookies()
    print('Cookies>>', cookies)
