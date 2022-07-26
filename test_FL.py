from pathlib import Path
import unittest
import unittest.mock as mock
import functools

from FL import Serial, Season, LibraryManager
from Console_ver import TXTVersion, State


def episodes_names(n=10):
    return [Path(str(i)) for i in range(1, n + 1)]


class TestSerial(unittest.TestCase):
    def setUp(self) -> None:
        self.current_path = Path.cwd()
        self.seasons = [Season(number=1, full_path=str(self.current_path), episodes_names=episodes_names(10)),
                        Season(number=2, full_path=str(self.current_path), episodes_names=episodes_names(10))]
        self.my_serial = Serial(name='test_serial', full_path=str(self.current_path), seasons=self.seasons)

    def test_current_episode_path(self):
        self.assertEqual(self.my_serial.current_episode_path, self.current_path / Path(self.seasons[0].episodes_names[0]))

    def test_increment_episode(self):
        init_episode_number, init_episode_number = self.my_serial.current_episode_number, self.my_serial.current_season_number
        self.my_serial.increment_episode()
        with self.subTest('Check episode incrementing'):
            self.assertEqual(self.my_serial.current_episode_number - 1, init_episode_number)

        with self.subTest('Check season not incrementing'):
            self.assertEqual(self.my_serial.current_season_number, init_episode_number)

    def test_increment_season(self):
        init_episode_number, init_episode_number = self.my_serial.current_episode_number, self.my_serial.current_season_number

        self.my_serial.current_episode_number = self.my_serial.max_episode_number
        self.my_serial.increment_episode()

        with self.subTest('Check episode incrementing'):
            self.assertEqual(self.my_serial.current_episode_number, init_episode_number)

        with self.subTest('Check season not incrementing'):
            self.assertEqual(self.my_serial.current_season_number - 1, init_episode_number)

    def test_max_increment(self):
        self.my_serial.current_season_number = self.my_serial.max_season_number
        self.my_serial.current_episode_number = self.my_serial.max_episode_number
        self.my_serial.increment_episode()

        with self.subTest('If watched'):
            self.assertTrue(self.my_serial.watched)

        with self.subTest('max season, episode checking'):
            self.assertEqual(self.my_serial.current_season_number, self.my_serial.max_season_number)
            self.assertEqual(self.my_serial.current_episode_number, self.my_serial.max_episode_number)


test_dir = r'D:\Entertainment\Movies'
episodes_in_serials = {'first': 10, 'second': 8}


def apply_path_patches(func):
    @functools.wraps(func)
    @mock.patch('pathlib.Path.iterdir',
                side_effect=[map(Path, ['first_serial', 'second_serial']),  # dir_with_serial
                             map(Path, ['1 season', '2 season']),  # last_season
                             episodes_names(episodes_in_serials['first']),  # max_episode_number
                             episodes_names(episodes_in_serials['first']),  # episodes_names in season

                             map(Path, ['1 season second_serial', '2 season second_serial']),  # last_season
                             episodes_names(episodes_in_serials['second']),  # max_episode_number
                             episodes_names(episodes_in_serials['second'])  # episodes_names in season
                             ])
    @mock.patch('pathlib.Path.is_dir', side_effect=[True, True, True, False])
    @mock.patch('pathlib.Path.is_file', return_value=True)
    def func_deco(*args, **kwargs):
        return func(*args, **kwargs)

    return func_deco


class TestLibraryManager(unittest.TestCase):

    def setUp(self) -> None:
        self.my_library_manager = LibraryManager(test_dir)

    @apply_path_patches
    def test_get_serials_from_dir(self, *args, **kwargs):
        self.my_library_manager.update_serials(force_update=True)

        with self.subTest('Serials len'):
            self.assertEqual(len(self.my_library_manager.current_serials), 2)

        for serial_number in ('first', 'second'):
            with self.subTest(f'Seasons in {serial_number}_serial'):
                self.assertEqual(self.my_library_manager[f'{serial_number}_serial'].max_season_number, 2)

            with self.subTest(f'episodes in {serial_number}_serial'):
                self.assertEqual(len(self.my_library_manager[f'{serial_number}_serial'].current_season.episodes_names),
                                 episodes_in_serials[serial_number])


class TestTxtVersion(unittest.TestCase):
    def setUp(self) -> None:
        self.txt_version = TXTVersion(test_dir)

    serial_index, season_number, episode_number = 1, 2, 3

    @mock.patch('builtins.input', return_value=f'{serial_index} {season_number} {episode_number}')
    @apply_path_patches
    # @mock.patch('builtins.input', return_value=' '.join(map(str, (serial_index, season_number, episode_number))))
    def test_editing(self, *args, **kwargs):
        self.txt_version.lib_manager.update_serials(force_update=True)
        serials_list = self.txt_version.lib_manager.get_serials_list()
        init_episode_number = serials_list[self.serial_index-1].current_episode_number
        init_season_number = serials_list[self.serial_index-1].current_season_number

        self.txt_version.editing()

        current_s_e = self.txt_version.lib_manager['first_serial'].current_season_episode
        self.assertNotEqual(current_s_e, (init_episode_number, init_season_number))
        self.assertEqual(current_s_e, (self.season_number, self.episode_number))


if __name__ == '__main__':
    unittest.main()
