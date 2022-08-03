import os
from pathlib import Path
import pickle
from dataclasses import dataclass


@dataclass
class Season:
    number: int
    """Starts with 1"""
    full_path: str | Path
    episodes_names: list[str | Path]
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
    def current_episode_name(self) -> str | Path:
        return self.current_season.episodes_names[self.current_episode_number - 1]

    @property
    def max_episode_number(self):
        """Last available episode"""
        return len(self.seasons[self.current_season_number - 1].episodes_names)

    @property
    def current_season_episode(self) -> tuple[int, int]:
        return self.current_season_number, self.current_episode_number

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
        return self.current_season.full_path / self.current_episode_name  # TODO replace with current_episode_name.full_path (it's PathLike)

    def __repr__(self):
        return f'{self.name}: s{self.current_season_number}e{self.current_episode_number}'


class LibraryManager:
    data_dir = Path('data')
    watched_path = data_dir / 'watched'

    def __init__(self, dir_with_serials):
        self.dir_with_serials = dir_with_serials
        self.current_serials = None
        """All serials"""
        self.serials_to_show = None
        """not watched serials"""

    @staticmethod
    def get_serials_from_dir(directory) -> dict:
        """
        :param directory: directory with serials
        :return: {serial_name: Serial, ...}
        """
        serials = {}
        for dir_with_serial in Path(directory).iterdir():
            if dir_with_serial.is_dir():
                seasons = []
                for season_number, season_path in enumerate(dir_with_serial.iterdir(), start=1):
                    episodes_names = [episode_path for episode_path in season_path.iterdir() if episode_path.is_file()]
                    seasons.append(Season(season_number, season_path, episodes_names))

                serials[dir_with_serial.name] = Serial(dir_with_serial.name, dir_with_serial, seasons)
        return serials

    def update_serials(self, force_update=False):
        if force_update:
            self.current_serials = self.get_serials_from_dir(self.dir_with_serials)
        else:
            try:
                with self.watched_path.open('rb') as f:
                    self.current_serials = pickle.load(f)
            except FileNotFoundError:
                self.current_serials = self.get_serials_from_dir(self.dir_with_serials)
                if not self.data_dir.exists():
                    self.data_dir.mkdir()

                with self.watched_path.open('wb') as f:
                    pickle.dump(self.current_serials, f)

    def get_serials_list(self, show_all=False) -> list[Serial] | None:
        if self.current_serials is None:
            self.update_serials()
            return self.get_serials_list()
        else:
            self.serials_to_show = []
            for serial_name, serial in self.current_serials.items():
                if not serial.watched:
                    self.serials_to_show.append(serial)
        return self.serials_to_show

    def dump_serials(self):
        if self.current_serials:
            with self.watched_path.open('wb') as f:
                pickle.dump(self.current_serials, f)
        else:
            pass

    def __getitem__(self, item) -> Serial:
        return self.current_serials[item]


def extract_digits(string_with_digits):
    digit = []
    for symbol in string_with_digits:
        if '1234567890'.find(symbol) != -1:
            digit.append(symbol)

    return int(''.join(digit)) if len(digit) != 0 else ''

