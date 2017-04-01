from urllib.parse import urlencode, urlparse
import requests
import math
import pandas as pd

AUTHORIZE_URL = 'https://oauth.vk.com/authorize'
VERSION = '5.63'
APP_ID = 5854786

def get_token():
    #получаем ссылку для получения токена

    auth_data = {
        'client_id': APP_ID,
        'display': 'mobile',
        'response_type': 'token',
        'scope': 'friends, groups',
        'v': VERSION,
    }
    print('Пройдите по ссылке и скопируйте новую url строку.')
    print('?'.join((AUTHORIZE_URL, urlencode(auth_data))))

def form_token():
    # Переходим по полученной ссылке и копируем ее в строку "token_url"
    token_url = input('ведите строку: ')  # в даннуя сроку

    o = urlparse(token_url)
    fragments = dict((i.split('=') for i in o.fragment.split('&')))
    access_token = fragments['access_token']
    return access_token

def form_id_page():
    # вводим id пользователя, по которому будем искать информацию
    need_id = input('введите id: ')  # id пищем сюда
    return  need_id

def get_friends(access_token, need_id):
    params = {'access_token': access_token,
              'user_id': need_id,
              'v': VERSION}

    response = requests.get('https://api.vk.com/method/friends.get', params)

    # получаем друзей пользователя
    friends = response.json()['response']['items']
    return friends

def get_follover(access_token, need_id):
    params_for_follovers = {'access_token': access_token,
                            'user_id': need_id,
                            'count': 1000,
                            'v': VERSION}

    response_follover = requests.get('https://api.vk.com/method/users.getFollowers', params_for_follovers)

    # получаем всех подписчиков пользователя
    follovers = response_follover.json()['response']['items']
    response_count_follover = response_follover.json()['response']['count']
    count_step = math.ceil(response_count_follover / 1000)

    offset = 0
    if (count_step > 1):
        while (count_step > 1):
            count_step = count_step - 1
            offset += 1000
            params_for_follovers = {'access_token': access_token,
                                    'user_id': need_id,
                                    'count': 1000,
                                    'offset': offset,
                                    'v': VERSION}

            try:
                response_follover = requests.get('https://api.vk.com/method/users.getFollowers', params_for_follovers)
                follovers += response_follover.json()['response']['items']
            except KeyError:
                count_step = count_step + 1
                offset -= 1000

    return follovers

def all_follovers_and_friends(friends, follovers):
    # получаем всех искомых пользователей
    ol_follov_and_friend = follovers + friends
    return ol_follov_and_friend

def get_groups_friends(access_token, id):
    params_for_groups_friends = {'access_token': access_token,
          'user_id' : id,
          'extended' : 1,
          #'count' : 7,
          'v': VERSION}
    response_groups_friends = requests.get('https://api.vk.com/method/groups.get', params_for_groups_friends)

    try:
        groups_info = response_groups_friends.json()['response']['items']

    except KeyError:
        if(response_groups_friends.json()['error']['error_code'] == 6):
            groups_info = get_groups_friends(access_token, id)
        groups_info = []
    return groups_info


def get_all_group(access_token, ol_follov_and_friend):
    # Получаем все группы пользователей
    group_friends = {}
    sum_friend_and_follov = len(ol_follov_and_friend)
    namber_iteration = 0
    print('Получение групп началось. Это займет продолжительное время.')

    for id in ol_follov_and_friend:
        namber_iteration += 1
        if (namber_iteration % 250 == 0):
            print('осталось: ' + str(sum_friend_and_follov - namber_iteration))

        groups_info = get_groups_friends(access_token, id)
        for group_inf_pers in groups_info:
            id_clab = group_inf_pers['id']
            try:
                group_friends[id_clab]['count'] += 1
                group_friends[id_clab]['id_user'].append(id)
            except KeyError:
                group_friends[id_clab] = {'name': group_inf_pers['name'], 'count': 1, 'id_user': [id]}

    print('готово!')
    return group_friends

def sort_in_pandas(group_friends):
    # подготавливаем записи для работы с pandas
    pp_group = []
    for key, id_gr in group_friends.items():
        pp_group.append({'id': key, 'name': id_gr['name'], 'count': id_gr['count']})

    pp_group_pd = pd.DataFrame(pp_group)
    top_group_selebrity = pp_group_pd.sort_values(by='count', ascending=False).head(100)
    return  top_group_selebrity

def write_in_file(top_group_selebrity, group_friends):
    myFile = 'top100.json' # пишем путь для сохранения в формате строки напр. '/Users/Anton/Desktop/python/net/top100.json'
    with open(myFile, 'w', encoding="utf-8") as f:
        n = 0
        f.write('[' + '\n')
        for index in top_group_selebrity['id']:
            n += 1
            next_group = group_friends[index]
            if (n < 100):
                f.write('{"id" : "' + str(index) + '", "title" : "' + str(next_group['name']).replace('"',
                        "'") + '", "count": "' + str(next_group['count']) + '"},' + '\n')
            if (n == 100):
                f.write('{"id" : "' + str(index) + '", "title" : "' + str(next_group['name']).replace('"',
                        "'") + '", "count": "' + str(next_group['count']) + '"}' + '\n')
                f.write(']')
                break

def start_parse():
    get_token()
    access_token = form_token()
    need_id = form_id_page()
    friends = get_friends(access_token, need_id)
    follovers = get_follover(access_token, need_id)
    ol_follov_and_friend = all_follovers_and_friends(friends, follovers)
    group_friends = get_all_group(access_token, ol_follov_and_friend)
    top_group_selebrity = sort_in_pandas(group_friends)
    write_in_file(top_group_selebrity, group_friends)


start_parse()
