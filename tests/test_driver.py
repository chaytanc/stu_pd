#vim: set noet noautoindent sw=4 ts=4
sys.path.append('../')
#XXX don't have py file yet
from driver import Driver

class TestBase():

    def setup(self):
    

    def test100_get_driver(self):
        dr = get_driver('Chr')
        assert dr, 'get_driver Chrome failed'
        dr = get_driver('Pha')
        assert dr, 'get_driver Phantom failed'
        dr = get_driver('Fi')
        assert dr, 'get_driver Firefox failed'
        dr = get_driver()
        assert dr, 'get_driver Firefox failed'

    def test200_setup_driver(self):
        #XXX how to test this?

    def test300_teardown_driver(self):
        #XXX how to test this?

