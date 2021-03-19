# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from instaparser.items import InstaparserItemLinks, InstaparserItemUsers, InstaparserItemPosts
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
    insta_pwd = '#PWD_INSTAGRAM_BROWSER:10:1615833714:AfhQAHpgyScVPcb7P/OWFtgsB3vtW1k0oAZDjeDBPbZIN6VmiPfH48YprZJPiIOKDUe6b9XpG12o43wIAVkS+Om/bn2mZllbObbRXJeNH0XZB5/Z5o/3qk9dz8HrX02RwDhMrPUxq91qZc2XOA=='
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    parse_users = ['fushik1','3dprintus']      #Пользователь, у которого собираем посты. Можно указать список

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
            for parse_user in self.parse_users:

                yield response.follow(
                    # Переходим на желаемую страницу пользователя. Сделать цикл для кол-ва пользователей больше 2-ух
                    f'/{parse_user}',
                    callback=self.user_data_parse,
                    cb_kwargs={'username': parse_user})

    def user_data_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)  # Получаем id пользователя
        variables = {'id': user_id,  # Формируем словарь для передачи даных в запрос
                     'first': 12}  # 12 постов. Можно больше (макс. 50)
        item = InstaparserItemUsers(
            _id=user_id,
            username=username,
            profile_pic_url=self.fetch_profile_pic_url(response.text, username),
            full_name=self.fetch_full_name(response.text, username))

        yield item

        url_posts = f'{self.graphql_url}query_hash={self.posts_hash}&{urlencode(variables)}'  # Формируем ссылку для получения данных о постах
        yield response.follow(
            url_posts,
            callback=self.user_posts_parse,
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'variables': deepcopy(variables)}  # variables ч/з deepcopy во избежание гонок
        )

        url_links = f'{self.graphql_url}query_hash={self.following_hash}&{urlencode(variables)}'  # Формируем ссылку для получения данных о постах
        yield response.follow(
            url_links,
            callback=self.following_links_parse,
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'variables': deepcopy(variables)}  # variables ч/з deepcopy во избежание гонок
        )

        url_links = f'{self.graphql_url}query_hash={self.followers_hash}&{urlencode(variables)}'  # Формируем ссылку для получения данных о постах
        yield response.follow(
            url_links,
            callback=self.followers_links_parse,
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'variables': deepcopy(variables)}  # variables ч/з deepcopy во избежание гонок
        )

    def user_posts_parse(self, response: HtmlResponse, username, user_id,
                         variables):  # Принимаем ответ. Не забываем про параметры от cb_kwargs
        j_data = json.loads(response.text)
        posts = j_data.get('data').get('user').get('edge_owner_to_timeline_media').get('edges')  # Сами посты
        for post in posts:  # Перебираем посты, собираем данные
            item = InstaparserItemPosts(
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

    def followers_links_parse(self, response: HtmlResponse, username, user_id,
                              variables):  # Принимаем ответ. Не забываем про параметры от cb_kwargs
        j_data = json.loads(response.text)
        links = j_data.get('data').get('user').get('edge_followed_by').get('edges')  # Сами посты
        for link in links:  # Перебираем подписчиков, собираем данные
            item = InstaparserItemLinks(
                user_from=link['node']['id'],
                user_to=user_id)
            yield item

            item = InstaparserItemUsers(
                _id=link['node']['id'],
                username=link['node']['username'],
                profile_pic_url=link['node']['profile_pic_url'],
                full_name=link['node']['full_name'])
            yield item

        page_info = j_data.get('data').get('user').get('edge_followed_by').get('page_info')
        if page_info.get('has_next_page'):  # Если есть следующая страница
            variables['after'] = page_info['end_cursor']  # Новый параметр для перехода на след. страницу
            url_links = f'{self.graphql_url}query_hash={self.followers_hash}&{urlencode(variables)}'
            yield response.follow(
                url_links,
                callback=self.followers_links_parse,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables': deepcopy(variables)}
            )

    def following_links_parse(self, response: HtmlResponse, username, user_id,
                              variables):  # Принимаем ответ. Не забываем про параметры от cb_kwargs
        j_data = json.loads(response.text)
        links = j_data.get('data').get('user').get('edge_follow').get('edges')  # Сами посты
        for link in links:  # Перебираем подписки, собираем данные

            item = InstaparserItemLinks(
                user_to=link['node']['id'],
                user_from=user_id)
            yield item

            item = InstaparserItemUsers(
                _id=link['node']['id'],
                username=link['node']['username'],
                profile_pic_url=link['node']['profile_pic_url'],
                full_name=link['node']['full_name'])
            yield item

        page_info = j_data.get('data').get('user').get('edge_follow').get('page_info')
        if page_info.get('has_next_page'):  # Если есть следующая страница
            variables['after'] = page_info['end_cursor']  # Новый параметр для перехода на след. страницу
            url_links = f'{self.graphql_url}query_hash={self.following_hash}&{urlencode(variables)}'
            yield response.follow(
                url_links,
                callback=self.following_links_parse,
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
            id = json.loads(matched).get('id')
        except Exception as e:
            id = '0'
            print(e)
        return id

    # Получаем full_name желаемого пользователя
    def fetch_full_name(self, text, username):
        # try:
        #     matched = re.search(
        #         '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        #     ).group()
        #     full_name = json.loads(matched).get('full_name')
        # except Exception as e:
        #     full_name = ''
        #     print(e)
        return 'full_name'

    def fetch_profile_pic_url(self, text, username):
        # try:
        #     matched = re.search(
        #         '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        #     ).group()
        #     full_name = json.loads(matched).get('full_name')
        # except Exception as e:
        #     full_name = ''
        #     print(e)
        return 'profile_pic_url'