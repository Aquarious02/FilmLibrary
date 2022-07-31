import os
from pathlib import Path
import pickle
from dataclasses import dataclass
from enum import IntEnum, auto


@dataclass
class Season:
    number: int
    """Starts with 1"""
    full_path: str | Path
    episodes_names: list
    """Episodes names (relative, no absolute)"""

    def __post_init__(self):
        if type(self.full_path) is str:
            self.full_path = Path(self.full_path)


@dataclass
class Serial:
    name: str
    full_path: str | Path
    seasons: list[Season]
    current_season_number: int = 1
    """Last season user stopped at"""
    current_episode_number: int = 1
    """Last episode user stopped at"""
    watched: bool = False

    def __post_init__(self):
        if type(self.full_path) is str:
            self.full_path = Path(self.full_path)

    @property
    def current_season(self) -> Season:
        return self.seasons[self.current_season_number - 1]  # TODO make with dict (in post_init)?

    @property
    def current_episode_name(self) -> str:
        return self.current_season.episodes_names[self.current_episode_number - 1]

    @property
    def max_episode_number(self):
        """Last available episode"""
        return len(self.seasons[self.current_season_number - 1].episodes_names)

    @property
    def max_season_number(self):
        """Last available season"""
        return len(self.seasons)

    def increment_episode(self):
        if self.current_episode_number < self.max_episode_number:
            self.current_episode_number += 1
        else:
            if self.current_season_number < self.max_season_number:
                self.current_season_number += 1
                self.current_episode_number = 1
            else:
                self.watched = True

    def watch(self, next_episode=True):
        os.startfile(self.current_episode_path)
        if next_episode:
            self.increment_episode()

    @property
    def current_episode_path(self) -> str:
        return self.current_season.full_path / self.current_episode_name

    def __repr__(self):
        return f'{self.name}: s{self.current_season_number}e{self.current_episode_number}'


class LibraryManager:
    data_dir = 'data'

    class State(IntEnum):
        deciding = auto()
        watching = auto()
        editing = auto()

    def __init__(self, dir_with_serials):
        self.dir_with_serials = dir_with_serials
        self.current_serials = None
        self.serials_to_show = None
        self.current_state = self.State.deciding

    @staticmethod
    def get_serials_from_dir(directory) -> dict:
        """
        :param directory: directory with serials
        :return: {serial_name: Serial, ...}
        """
        serials = {}
        for dir_name in os.listdir(directory):
            full_serial_path = fr'{directory}\{dir_name}'
            if os.path.isdir(full_serial_path):
                last_season = os.listdir(full_serial_path)[-1]
                last_season_number = extract_digits(last_season)

                max_episode_number = len(os.listdir(fr'{full_serial_path}\{last_season}'))

                seasons = []
                for season_number, season_name in enumerate(os.listdir(full_serial_path), start=1):
                    full_season_path = fr'{full_serial_path}\{season_name}'
                    seasons.append(Season(number=season_number, full_path=full_season_path,
                                          episodes=list(os.listdir(full_season_path))))

                serials[dir_name] = Serial(name=dir_name, full_path=full_serial_path, max_season=last_season_number,
                                           max_episode=max_episode_number, seasons=seasons)
        return serials

    def update_serials(self):
        try:
            with open(f'{self.data_dir}/watched', 'rb') as f:
                self.current_serials = pickle.load(f)
        except FileNotFoundError:
            self.current_serials = self.get_serials_from_dir(self.dir_with_serials)
            if not os.path.exists(self.data_dir):
                os.mkdir(self.data_dir)

            with open(f'{self.data_dir}/watched', 'wb') as f:
                pickle.dump(self.current_serials, f)

    def show_serials_list(self):
        if self.current_serials:
            self.serials_to_show = []
            print('В вашей фильмотеке содержатся следующие сериалы:')
            for serial_name, serial in self.current_serials.items():
                if not serial.watched:
                    self.serials_to_show.append(serial)
                    print(
                        f'{len(self.serials_to_show)}. {serial_name}. (Остановились на s{serial.current_season_number}.e{serial.current_season_number})')
        else:
            print('В вашей фильмотеке нет сериалов :(')

    def dump_serials(self):
        if self.current_serials:
            with open(f'{self.data_dir}/watched', 'wb') as f:
                pickle.dump(self.current_serials, f)
        else:
            pass

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

    def txt_version(self):
        self.update_serials()

        self.show_serials_list()

        command = input('Введите позицию медиа\n')
        old_index = None
        while command != 'n' and command != 'т':
            next_episode = True
            if old_index is None:
                if '-' in command:
                    next_episode = False
                    command = command.replace('-', '')
                index = int(command)
                old_index = index
            else:
                index = old_index

            self.serials_to_show[index - 1].watch(next_episode)
            self.dump_serials()

            command = input('Включить следующую серию? (enter/n)\n')


def extract_digits(string_with_digits):
    digit = []
    for symbol in string_with_digits:
        if '1234567890'.find(symbol) != -1:
            digit.append(symbol)

    return int(''.join(digit)) if len(digit) != 0 else ''


if __name__ == '__main__':
    directory = r'D:\Entertainment\Movies'
    # txt_version(directory)

    library_manager = LibraryManager(directory)
    library_manager.txt_version()
