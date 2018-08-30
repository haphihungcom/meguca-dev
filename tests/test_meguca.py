import time

import pytest
import freezegun

from meguca import meguca

class TestMeguca():
    def test_prepare(self):
        meguca_ins = meguca.Meguca('tests/config_for_testing.ini')

        assert meguca_ins.scheduler.get_jobs()[0].name == 'Test plugin 3'

    @freezegun.freeze_time('2018-01-01', tick=True)
    def test_run(self):
        meguca_ins = meguca.Meguca('tests/config_for_testing.ini')
        meguca_ins.run()

        time.sleep(4)

        assert meguca_ins.data['TestKey2'] == 'TestVal'
