import unittest
import unittest.mock as mock
# import mock
from FL import *


def episodes_names(n=10):
    return list(map(str, range(1, n + 1)))


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


class TestLibraryManager(unittest.TestCase):
    test_dir = r'D:\Entertainment\Movies'
    episodes_in_serials = {'first': 10, 'second': 8}

    def setUp(self) -> None:
        self.my_library_manager = LibraryManager(self.test_dir)

    @mock.patch('os.listdir', side_effect=[['first_serial', 'second_serial'],  # dir_name_with_serial
                                           ['1 season', '2 season'],  # last_season
                                           episodes_names(episodes_in_serials['first']),  # max_episode_number
                                           episodes_names(episodes_in_serials['first']),  # episodes_names in season

                                           ['1 season second_serial', '2 season second_serial'],  # last_season
                                           episodes_names(episodes_in_serials['second']),  # max_episode_number
                                           episodes_names(episodes_in_serials['second'])  # episodes_names in season
                                           ])
    @mock.patch('os.path.isdir', side_effect=[True, True, True, False])
    def test_get_serials_from_dir(self, mock_dir, mock_isdir):
        self.my_library_manager.update_serials(force_update=True)
        # serials = self.my_library_manager.get_serials_from_dir(self.test_dir)
        with self.subTest('Serials len'):
            self.assertEqual(len(self.my_library_manager.current_serials), 2)

        with self.subTest('episodes in serials'):
            self.assertEqual(len(self.my_library_manager['first_serial'].current_season.episodes_names), self.episodes_in_serials['first'])
            self.assertEqual(len(self.my_library_manager['second_serial'].current_season.episodes_names), self.episodes_in_serials['second'])


if __name__ == '__main__':
    unittest.main()
