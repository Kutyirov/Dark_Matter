from bs4 import BeautifulSoup
import requests
import threading
import pprint


def get_app_info(name, url, global_info):
    app_info = {}
    app_text = (requests.get(url)).text
    app_soup = BeautifulSoup(app_text, features="html.parser")

    # определение категории
    categories_classes = app_soup.find(
        "a", {"class": "hrTbp R8zArc", "itemprop": "genre"})
    app_info['category'] = categories_classes.string

    # определение количества оценок
    num_of_ratings_class = app_soup.find(
        lambda tag: ("ratings" in str(tag.get("aria-label"))))
    if (num_of_ratings_class is not None):
        app_info['num_of_ratings'] = num_of_ratings_class.string
    else:
        app_info['num_of_ratings'] = 0

    # находим последнее обновление
    last_update = app_soup.find(lambda tag: tag.name == 'div' and
                                tag.get('class') == ['BgcNfc'] and
                                tag.string == "Updated")
    app_info['last_update'] = last_update.next_sibling.string

    # находим описание
    description_class = app_soup.find("div", {"jsname": "sngebd"})
    app_info['description'] = description_class.text

    global_info[name] = app_info


if __name__ == '__main__':
    print('Введите приложение для поиска: ', end='')
    input_app = input()
    url_for_request = "https://play.google.com/store/search?q=" + \
        str(input_app) + "&c=apps"
    r = requests.get(url_for_request)

    soup = BeautifulSoup(r.text, features="html.parser")
    with open('test.txt', 'w', encoding="utf-8") as output_file:
        output_file.write(soup.prettify())

    # получаем названия приложений
    names_classes = soup.find_all("div", {"class": "WsMG1c nnK0zc"})
    names = []
    for name in names_classes:
        names.append(name.string)

    # получаем автора
    author_classes = soup.find_all(lambda tag: tag.name ==
                                   'div' and tag.get('class') == ['KoLSrc'])
    authors = []

    for author in author_classes:
        authors.append(author.string)

    # получаем ссылки
    url_classes = soup.find_all("div", {"class": "b8cIId ReQCgd Q9MA7b"})
    urls = []
    for url in url_classes:
        urls.append(url.a['href'])

    # получаем средние оценки
    rating_classes = soup.find_all("div", {"class": "pf5lIe"})
    ratings = []
    for rating in rating_classes:
        ratings.append(rating.div['aria-label'])

    apps = [list(tup) for tup in zip(names, urls)]

    potocs = []
    global_info = {}
    for app in apps:
        app_url = "https://play.google.com" + app[1]
        potoc = threading.Thread(
            target=get_app_info, args=(app[0], app_url, global_info))
        potocs.append(potoc)
        potoc.start()

    for potoc in potocs:
        potoc.join()

    # объединим все данные в один словарь global information

    for index in range(len(names)):
        global_info[names[index]]['author'] = authors[index]
        global_info[names[index]]['href'] = urls[index]
        global_info[names[index]]['rating'] = ratings[index]

    # удалим все приложения без кодового слова
    apps_exist = {}
    for name in global_info:
        flag = False
        code_words = {input_app}
        code_words.add(input_app[0].upper() + input_app[1:])
        code_words.add(input_app[0].lower() + input_app[1:])
        for word in code_words:
            if (word in name) or \
                    (word in global_info[name]['author']) or \
                    (word in global_info[name]['description']) or \
                    (word in global_info[name]['category']):
                flag = True
        if flag is True:
            apps_exist[name] = global_info[name]

    # теперь все интересующие нас приложения находятся в словаре apps_exist
    pprint.pprint(apps_exist)

    # https://play.google.com/_/PlayStoreUi/data/batchexecute?rpcids=qnKhOb&f.sid=8518470991209432701&bl=boq_playuiserver_20210411.08_p0&hl=ru&authuser=0&soc-app=121&soc-platform=1&soc-device=1&_reqid=482919&rt=c
    # https://play.google.com/_/PlayStoreUi/data/batchexecute?rpcids=qnKhOb&f.sid=8518470991209432701&bl=boq_playuiserver_20210411.08_p0&hl=ru&authuser=0&soc-app=121&soc-platform=1&soc-device=1&_reqid=382919&rt=c
    # отличаются в конце цифрами 3 и 4
    # по запросу "кино"
    # https://play.google.com/_/PlayStoreUi/data/batchexecute?rpcids=qnKhOb&f.sid=-8934350538362705477&bl=boq_playuiserver_20210411.08_p0&hl=ru&authuser=0&soc-app=121&soc-platform=1&soc-device=1&_reqid=183843&rt=c
    # изменился sid и последние цифры
