from FL import *
from enum import IntEnum


class TXTVersion:
    class State(IntEnum):
        deciding = auto()
        watching = auto()
        editing = auto()

    def __init__(self, dir_with_serials):
        self.lib_manager = LibraryManager(dir_with_serials)
        """library manager"""
        self.current_state = self.State.deciding

    def show_serials_list(self, to_update=False, show_all=False):
        """
        Get list with current serials objects
        :param to_update: update info from dir if True
        :param show_all: show watched if True
        """
        if to_update:
            self.lib_manager.update_serials(force_update=True)
        serials_list = self.lib_manager.get_serials_list(show_all)
        print('В вашей фильмотеке содержатся следующие сериалы:')
        if serials_list:
            for index, serial in enumerate(serials_list, start=1):
                if not serial.watched:
                    print(f'{index}. {serial.name}. (Остановились на s{serial.current_season_number}.e{serial.current_episode_number})')
        else:
            print('В вашей фильмотеке нет сериалов :(')

    def process_state(self):
        match self.current_state:
            case self.State.deciding:
                command = input('Введите позицию медиа\n')
                if command != 'n' and command != 'т':
                    self.current_state = self.State.watching
            case self.State.watching:
                pass
            case self.State.editing:
                pass

    def run(self):
        self.show_serials_list(to_update=True)

        command = input('Введите позицию медиа\n')
        old_index = None
        while command != 'n' and command != 'т':
            next_episode = True
            if old_index is None:
                if '-' in command:
                    next_episode = False
                    command = command.replace('-', '')
                try:
                    index = int(command)
                except Exception as e:
                    input(f'{e}.\nEnter to close')
                    break
                old_index = index
            else:
                index = old_index

            self.lib_manager.serials_to_show[index - 1].watch(next_episode)
            self.lib_manager.dump_serials()

            command = input('Включить следующую серию? (enter/n)\n')


if __name__ == '__main__':
    directory = r'D:\Entertainment\Movies'

    txt_version = TXTVersion(directory)
    txt_version.run()
