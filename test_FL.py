import unittest
from FL import *


class TestSerial(unittest.TestCase):
    def setUp(self) -> None:
        self.current_path = Path.cwd()
        self.seasons = [Season(number=1, full_path=str(self.current_path), episodes_names=list(map(str, range(1, 10)))),
                        Season(number=2, full_path=str(self.current_path), episodes_names=list(map(str, range(1, 10))))]
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





if __name__ == '__main__':
    unittest.main()
