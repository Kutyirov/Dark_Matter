import whois
import threading
import itertools
import sys
import contextlib


class interface(object):
    def __init__(self, domain):
        self.my_domain = domain_checker(domain)  # объект для работы с доменами
        self.answer = ''                         # ответ пользователя
        self.flag_activity = True                # флаг цикла меню
        self.menu_size = 8                       # размер меню

    def show_commands(self):
        print("Доступны следующие команды")
        print('1 - Добавить одну букву в конец домена')
        print('2 - Замена в домене символов похожими')
        print('3 - Выделение в домене поддомена точкой')
        print('4 - Удаление одного символа')
        print('5 - Проверить существующие домены')
        print('6 - Вывести существующие домены')
        print('7 - Вывести сгенерированные домены')
        print('8 - Выход')

    # циклим интерфейс
    def interface_cycle(self):
        while (self.flag_activity):
            self.get_answer()
        self.flag_activity = True

    # считываем домен пользователя и вызываем нужную функцию
    def get_answer(self):
        self.show_commands()
        print('Ваш ответ: ', end='')
        self.answer = input()
        if (not self.answer.isdigit()):
            return
        if (int(self.answer) < 1 or int(self.answer) > self.menu_size):
            return

        {1: self.my_domain.add_lit,
         2: self.my_domain.add_homoglyph,
         3: self.my_domain.add_point,
         4: self.my_domain.del_char,
         5: self.my_domain.parallel_check,
         6: self.my_domain.print_exist_domains,
         7: self.my_domain.print_domain,
         8: self.interface_exit,
         }.get(int(self.answer))()

    # когда нужно выходим
    def interface_exit(self):
        self.flag_activity = False


class domain_checker(object):
    def __init__(self, domain):
        self.domains = {domain}     # множество сгенерированных доменов
        self.domain_exist = set()   # множество существующих доменов

    # функция добавления буквы в конец домена
    def add_lit(self):
        domain_set = set()
        for domain in self.domains:
            for lit in range(97, 123):
                domain_set.add(domain + chr(lit))
        self.domains = set.union(self.domains, domain_set)

    # функция замены символов похожими
    def add_homoglyph(self):
        # множество содержит похожие символы
        homoglyph_set = {'0': 'O', '1': 'l', 'l': '1', 'O': '0'}
        domain_set = set()
        for domain in self.domains:
            positions = []
            position = 0
            # определим на каких позициях находятся символы для замены
            for char in domain:
                if char in homoglyph_set:
                    positions.append(position)
                position += 1

            final_seq = set()
            # сгенерируем множество всех возможных последовательностей,
            # в которых 0 означает, что символ на похожий менять не нужно
            # 1 - что нужно
            for i in range(len(positions)+1):
                seq = '0'*i + '1'*(len(positions) + 1 - i)
                sequences = itertools.permutations(seq, r=len(positions))
                for sequence in sequences:
                    final_seq.add(sequence)

            # используя сгенерированные последовательности получим новые домены
            for sequence in final_seq:
                new_domain = ''
                prev_position = 0
                for position in positions:
                    new_domain += domain[prev_position:position]
                    if sequence[positions.index(position)] == '0':
                        new_domain += domain[position]
                    else:
                        new_domain += homoglyph_set.get(
                            domain[position])
                    prev_position = position + 1
                new_domain += domain[positions[-1]+1:]
                domain_set.add(new_domain)

        self.domains = set.union(self.domains, domain_set)

    # функция выделения поддомена точкой
    def add_point(self):
        domain_set = set()
        for domain in self.domains:
            for index in range(1, len(domain)):
                domain_set.add(domain[:index] + '.' + domain[index:])
        self.domains = set.union(self.domains, domain_set)

    # функция удаления одного символа из домена
    def del_char(self):
        domain_set = set()
        for domain in self.domains:
            if len(domain) == 1:
                continue
            for index in range(len(domain)):
                domain_set.add(domain[:index] + domain[index+1:])
        self.domains = set.union(self.domains, domain_set)

    # функция проверки занятости домена
    def check_domain(self, domain):
        try:    # если домен существует, то запомним его
            data = whois.whois(domain)
            if data['domain_name'] is not None:
                self.domain_exist.add(domain)
        except whois.parser.PywhoisError:
            pass  # если не существует - неинтересно

    # функция параллельной проверки доменов
    def parallel_check(self):
        zones = (
            '.com', '.ru', '.net', '.org', '.info', '.cn', '.es', '.top',
            '.au', '.pl', '.it', '.uk', '.tk', '.ml', '.ga', '.cf', '.us',
            '.xyz', '.site', '.win', '.bid',
        )
        potocs = []
        original_stdout = sys.stdout
        sys.stdout = open('log.txt', 'w')
        # добавив в каждый домен каждую зону создадим поток, проверяющий домен
        for domain in self.domains:
            for zone in zones:
                end_domain = domain + zone
                potoc = threading.Thread(
                    target=self.check_domain, args=(end_domain,))
                potocs.append(potoc)
                potoc.start()
        for potoc in potocs:
            potoc.join()
        sys.stdout = original_stdout
        self.print_exist_domains()

    # функция для вывода сгенерированных доменов
    def print_domain(self):
        sorted_domains = list(self.domains)
        sorted_domains.sort()
        for domain in sorted_domains:
            print(domain)

    # функция вывода существующих доменов
    def print_exist_domains(self):
        sorted_domains = list(self.domain_exist)
        sorted_domains.sort()
        print("Список существующих доменов:")
        for domain in sorted_domains:
            print(domain)


if __name__ == '__main__':
    print('Введите домен: ', end='')
    my_interface_class = interface(input())
    my_interface_class.interface_cycle()
