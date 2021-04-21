from datetime import datetime
import requests
import socket
import threading
import re
import ipaddress
import uncurl


class interface(object):
    def __init__(self, ip_net, ports):
        if (self.check_ip(ip_net) is False):
            print('Вы ввели не подсеть, выберите пункт 1')
            self.ip_net = None
        else:
            self.ip_net = ipaddress.IPv4Network(ip_net)  # адрес подсети
        self.ports = set()                               # сканируемые порты
        self.get_ports(ports)
        self.flag_activity = True                        # для цикла меню
        self.answer = ''                                 # ответ пользователя
        self.menu_size = 7                               # число пунктов меню
        self.open_ports = []                             # открытые порты

    # вызываем меню
    def interface_cycle(self):
        while (self.flag_activity):
            self.get_answer()
        self.flag_activity = True

    def who_is_listening(self):
        # response = requests.head('http://mail.ru/')
        print('Введите ip для проверки: ', end='')
        ip_listening = input()
        ip_address = ip_address = r'([0-1]?([0-9]?){2}|2[0-4][0-9]|25[0-5])'\
            r'(\.([0-1]?([0-9]?){2}|2[0-4][0-9]|25[0-5])){3}'
        if (re.fullmatch(ip_address, ip_listening) is None):
            print('ip не обнаружен, будет использоваться 192.168.0.1')
            ip_listening = '192.168.0.1'
        if (self.scan_port(ip_listening, 80)):
            response = requests.head('http://' + ip_listening + ':80')
            if ('Server' in response.headers):
                print(ip_listening + ':80 прослушивается с помощью ' +
                      response.headers['Server'])
            else:
                print('по 80 порту информации нет')
        else:
            print('80 порт закрыт')
        if (self.scan_port(ip_listening, 443)):
            response = requests.head('http://' + ip_listening + ':443')
            if ('Server' in response.headers):
                print(ip_listening + ':443 прослушивается с помощью' +
                      response.headers['Server'])
            else:
                print('по 443 порту информации нет')
        else:
            print('443 порт закрыт')

    def show_commands(self):
        print("Доступны следующие команды")
        print('1 - Ввести новый ip сети')
        print('2 - Ввести новые порты')
        print('3 - Показать открытые порты')
        print('4 - Показать кто слушает 80 и 443 порт')
        print('5 - Вывести текущий ip сети')
        print('6 - Вывести проверяемые порты')
        print('7 - Выход')

    # выводим подсеть, которую будем сканировать
    def print_ip(self):
        if self.ip_net is None:
            print('Ip не задан, выберите пункт 1')
            return
        print(str(self.ip_net))

    # выводим порты, которые будем проверять
    def print_ports(self):
        for port in self.ports:
            print(port)

    # из строки портов, получаем список
    def get_ports(self, input_ports):
        input_ports += '.'
        number = ''
        self.ports = set()
        for chars in input_ports:
            if chars.isdigit():
                number += chars
            elif number != '':
                self.ports.add(int(number))
                number = ''

    # получив ответ вызываем нужную функцию
    def get_answer(self):
        self.show_commands()
        print('Ваш ответ: ', end='')
        self.answer = input()
        if (not self.answer.isdigit()):
            return
        if (int(self.answer) < 1 or int(self.answer) > self.menu_size):
            return
        {1: self.new_ip,
         2: self.new_ports,
         3: self.scan_port_parallel,
         4: self.who_is_listening,
         5: self.print_ip,
         6: self.print_ports,
         7: self.interface_exit,
         }.get(int(self.answer))()

    # когда хотим выйти опускаем флаг
    def interface_exit(self):
        self.flag_activity = False

    # для каждого ip и порта создаем свой поток
    def scan_port_parallel(self):
        if self.ip_net is None:
            print('Ip не задан, выберите пункт 1')
            return
        self.open_ports = []
        potocs = []
        for ip in self.ip_net:
            # print(ip)
            for port in self.ports:
                # print(ip, port)
                potoc = threading.Thread(
                    target=self.scan_port, args=(str(ip), int(port)))
                potocs.append(potoc)
                potoc.start()
        for potoc in potocs:
            potoc.join()
        if (len(self.open_ports) == 0):
            print('\nОткрытых портов не обнаружено\n')
        else:
            for open_port in self.open_ports:
                print(open_port)

    # сканируем один порт
    def scan_port(self, ip, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        try:  # если получилось установить связь, то запоминаем порт
            connect = sock.connect((ip, port))
            # print('Port :', port, ' its open.')
            self.open_ports.append(
                'ip ' + str(ip) + ' с портом ' + str(port) + ' открыт')

            sock.close()
        except Exception:
            pass  # иначе нам неинтересно
            return False
        return True

    # проверяем, что ip сети в понятном виде
    def check_ip(self, ip):
        ip_net_address = r'([0-1]?([0-9]?){2}|2[0-4][0-9]|25[0-5])'\
            r'(\.([0-1]?([0-9]?){2}|2[0-4][0-9]|25[0-5])){3}'\
            r'(\/(([0-2]?[0-9]?)|(3[0-2])))'
        # ip_net_address = r'(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9][0-9]|[0-9])'\
        #             r'(\.(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9][0-9]|[0-9])){3}'
        if (re.fullmatch(ip_net_address, ip) is not None):
            return True
        return False

    # для ввода нового ip
    def new_ip(self):
        print('Введите новый ip сети: ', end='')
        new_ip = input()
        while (self.check_ip(new_ip) is False):
            print('Вы ввели не ip сети попробуйте еще раз')
            print('Новый ip: ', end='')
            new_ip = input()
        self.ip_net = ipaddress.IPv4Network(new_ip)

    # для ввода новых портов для сканирования
    def new_ports(self):
        print('Введите новые порты: ', end='')
        ports = input()
        self.get_ports(ports)


if __name__ == '__main__':
    print("Ожидаю адрес сети: ", end='')
    ip = input()
    print("Ожидаю порты: ", end='')
    input_ports = input()
    my_interface_class = interface(ip, input_ports)
    my_interface_class.interface_cycle()
