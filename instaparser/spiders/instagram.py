# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from instaparser.items import InstaparserItem, InstaparserItemFollowers, InstaparserItemFollowing
import re
import json
from urllib.parse import urlencode
from copy import deepcopy


class InstagramSpider(scrapy.Spider):
    # атрибуты класса
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://instagram.com/']
    insta_login = 'kasws3'
    insta_pwd = '#PWD_INSTAGRAM_BROWSER'
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    parse_user = 'fushik1'  # ,'3dprintus']      #Пользователь, у которого собираем посты. Можно указать список

    graphql_url = 'https://www.instagram.com/graphql/query/?'

    followers_hash = '5aefa9893005572d237da5068082d8d5'
    following_hash = '3dec7e2c57367ef3da3d987d89f9dbc8'
    posts_hash = '003056d32c2554def87228bc3fd9668a'  # hash для получения данных по постах с главной страницы

    def parse(self, response: HtmlResponse):  # Первый запрос на стартовую страницу
        csrf_token = self.fetch_csrf_token(response.text)  # csrf token забираем из html
        yield scrapy.FormRequest(  # заполняем форму для авторизации
            self.inst_login_link,
            method='POST',
            callback=self.user_parse,
            formdata={'username': self.insta_login, 'enc_password': self.insta_pwd},
            headers={'X-CSRFToken': csrf_token}
        )

    def user_parse(self, response: HtmlResponse):
        j_body = json.loads(response.text)

        if j_body['authenticated']:  # Проверяем ответ после авторизации
            # for parse_user in self.parse_users:
            yield response.follow(
                # Переходим на желаемую страницу пользователя. Сделать цикл для кол-ва пользователей больше 2-ух
                f'/{self.parse_user}',
                callback=self.user_data_parse,
                cb_kwargs={'username': self.parse_user})

            yield response.follow(
                # Переходим на желаемую страницу пользователя. Сделать цикл для кол-ва пользователей больше 2-ух
                f'/{self.parse_user}',
                callback=self.followers_data_parse,
                cb_kwargs={'username': self.parse_user})

            yield response.follow(
                # Переходим на желаемую страницу пользователя. Сделать цикл для кол-ва пользователей больше 2-ух
                f'/{self.parse_user}',
                callback=self.following_data_parse,
                cb_kwargs={'username': self.parse_user})

    def followers_data_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)  # Получаем id пользователя
        variables = {'id': user_id,  # Формируем словарь для передачи даных в запрос
                     'first': 12}  # 12 постов. Можно больше (макс. 50)
        url_posts = f'{self.graphql_url}query_hash={self.followers_hash}&{urlencode(variables)}'  # Формируем ссылку для получения данных о постах
        yield response.follow(
            url_posts,
            callback=self.followers_posts_parse,
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'variables': deepcopy(variables)}  # variables ч/з deepcopy во избежание гонок
        )

    def following_data_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)  # Получаем id пользователя
        variables = {'id': user_id,  # Формируем словарь для передачи даных в запрос
                     'first': 12}  # 12 постов. Можно больше (макс. 50)
        url_posts = f'{self.graphql_url}query_hash={self.following_hash}&{urlencode(variables)}'  # Формируем ссылку для получения данных о постах
        yield response.follow(
            url_posts,
            callback=self.following_posts_parse,
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'variables': deepcopy(variables)}  # variables ч/з deepcopy во избежание гонок
        )

    def user_data_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)  # Получаем id пользователя
        variables = {'id': user_id,  # Формируем словарь для передачи даных в запрос
                     'first': 12}  # 12 постов. Можно больше (макс. 50)
        url_posts = f'{self.graphql_url}query_hash={self.posts_hash}&{urlencode(variables)}'  # Формируем ссылку для получения данных о постах
        yield response.follow(
            url_posts,
            callback=self.user_posts_parse,
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'variables': deepcopy(variables)}  # variables ч/з deepcopy во избежание гонок
        )

    def user_posts_parse(self, response: HtmlResponse, username, user_id,
                         variables):  # Принимаем ответ. Не забываем про параметры от cb_kwargs
        j_data = json.loads(response.text)
        posts = j_data.get('data').get('user').get('edge_owner_to_timeline_media').get('edges')  # Сами посты
        for post in posts:  # Перебираем посты, собираем данные
            item = InstaparserItem(
                user_id=user_id,
                photo=post['node']['display_url'],
                likes=post['node']['edge_media_preview_like']['count'],
                post=post['node']
            )
            yield item  # В пайплайн

        page_info = j_data.get('data').get('user').get('edge_owner_to_timeline_media').get('page_info')
        if page_info.get('has_next_page'):  # Если есть следующая страница
            variables['after'] = page_info['end_cursor']  # Новый параметр для перехода на след. страницу
            url_posts = f'{self.graphql_url}query_hash={self.posts_hash}&{urlencode(variables)}'
            yield response.follow(
                url_posts,
                callback=self.user_posts_parse,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables': deepcopy(variables)}
            )



    def followers_posts_parse(self, response: HtmlResponse, username, user_id,
                              variables):  # Принимаем ответ. Не забываем про параметры от cb_kwargs
        j_data = json.loads(response.text)
        posts = j_data.get('data').get('user').get('edge_followed_by').get('edges')  # Сами посты
        for post in posts:  # Перебираем посты, собираем данные
            item = InstaparserItemFollowers(
                _id=post['node']['id'],
                user_to=user_id,
                username=post['node']['username'],
                url=post['node']['profile_pic_url'],
                full_name=post['node']['full_name']

            )
            yield item  # В пайплайн

        page_info = j_data.get('data').get('user').get('edge_followed_by').get('page_info')
        if page_info.get('has_next_page'):  # Если есть следующая страница
            variables['after'] = page_info['end_cursor']  # Новый параметр для перехода на след. страницу
            url_posts = f'{self.graphql_url}query_hash={self.followers_hash}&{urlencode(variables)}'
            yield response.follow(
                url_posts,
                callback=self.followers_posts_parse,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables': deepcopy(variables)}
            )



    def following_posts_parse(self, response: HtmlResponse, username, user_id,
                              variables):  # Принимаем ответ. Не забываем про параметры от cb_kwargs
        j_data = json.loads(response.text)
        posts = j_data.get('data').get('user').get('edge_follow').get('edges')  # Сами посты
        for post in posts:  # Перебираем посты, собираем данные
            item = InstaparserItemFollowing(
                _id=post['node']['id'],
                user_from=user_id,
                username=post['node']['username'],
                url=post['node']['profile_pic_url'],
                full_name=post['node']['full_name']
            )
            yield item
        page_info = j_data.get('data').get('user').get('edge_follow').get('page_info')
        if page_info.get('has_next_page'):  # Если есть следующая страница
            variables['after'] = page_info['end_cursor']  # Новый параметр для перехода на след. страницу
            url_posts = f'{self.graphql_url}query_hash={self.following_hash}&{urlencode(variables)}'
            yield response.follow(
                url_posts,
                callback=self.following_posts_parse,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables': deepcopy(variables)}
            )



    # Получаем токен для авторизации
    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    # Получаем id желаемого пользователя
    def fetch_user_id(self, text, username):
        try:
            matched = re.search(
                '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
            ).group()
            id =json.loads(matched).get('id')
        except Exception as e:
            id ='0'
            print(e)
        return id
