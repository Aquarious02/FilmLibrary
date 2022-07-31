import unittest
from FL import *


class TestSerial(unittest.TestCase):
    def setUp(self) -> None:
        self.current_path = Path.cwd()
        self.one_season = Season(number=1, full_path=str(self.current_path), episodes=list(map(str, range(1, 10))))
        self.my_serial = Serial(name='test_serial', full_path=str(self.current_path), seasons=[self.one_season],
                                max_season=1, max_episode=len(self.one_season.episodes))

    def test_current_episode_path(self):
        self.assertEqual(self.my_serial.current_episode_path, self.current_path / Path(self.one_season.episodes[0]))


if __name__ == '__main__':
    unittest.main()
