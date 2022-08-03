from enum import IntEnum, auto

from FL import LibraryManager


class State(IntEnum):
    deciding = auto()
    watching = auto()
    editing = auto()
    helping = auto()
    stop = auto()


class TXTVersion:
    stop_word = {'n', 'т', 'stop'}

    def __init__(self, dir_with_serials):
        self.lib_manager = LibraryManager(dir_with_serials)
        """library manager"""
        self.current_state = State.deciding
        self.current_index = None

    def show_serials_list(self, to_update=False, show_all=False):
        """
        Get list with current serials objects
        :param to_update: update info from dir if True
        :param show_all: show watched if True
        """
        if to_update:
            self.lib_manager.update_serials(force_update=True)
        serials_list = self.lib_manager.get_serials_list(show_all)
        if serials_list:
            print('В вашей фильмотеке содержатся следующие сериалы:')
            for index, serial in enumerate(serials_list, start=1):
                if not serial.watched:
                    print(f'{index}. {serial.name}. (Остановились на s{serial.current_season_number}.e{serial.current_episode_number})')
        else:
            print('В вашей фильмотеке нет сериалов :(')

    def process_state(self):
        match self.current_state:
            case State.deciding:
                self.deciding()
            case State.watching:
                self.watching()
            case State.editing:
                self.editing()
            case State.helping:
                self.helping()
            case State.stop:
                self.stop()

    def deciding(self):
        command = input('Введите позицию медиа\n')
        if command.lower() not in self.stop_word:
            self.current_state = State.watching
            next_episode = True
            if '-' in command:
                next_episode = False
                command = command.replace('-', '')
            try:
                self.current_index = int(command)
                self.lib_manager.serials_to_show[self.current_index - 1].watch(next_episode)
                self.lib_manager.dump_serials()
            except Exception as e:
                input(f'{e}.\nEnter to close')
                self.stop()
        else:
            self.stop()

    def watching(self):
        command = input('Включить следующую серию? (enter/n)\n')
        if command.lower() not in self.stop_word:
            self.lib_manager.serials_to_show[self.current_index - 1].watch()
        else:
            self.current_state = State.deciding

    def editing(self):
        command = input('Введите позицию сериала, новые номер сезона и эпизода через пробел\n')
        if command.lower() not in self.stop_word:
            index, new_season, new_episode = list(map(int, command.split()))
            self.lib_manager.serials_to_show[index - 1].current_season_number = new_season
            self.lib_manager.serials_to_show[index - 1].current_episode_number = new_episode
        else:
            self.current_state = State.editing

    def helping(self):
        pass

    def run(self):
        self.lib_manager.update_serials()

        self.current_state = State.deciding
        self.show_serials_list()

        while self.current_state != State.stop:
            self.process_state()

    def stop(self):
        self.current_state = State.stop


if __name__ == '__main__':
    directory = r'D:\Entertainment\Movies'

    txt_version = TXTVersion(directory)
    txt_version.run()
