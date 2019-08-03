from scraper import AngelListScraper

class Main():
    # CONSTANTS
    signal_pair_list = [(0, 1), (1, 2), (2, 3), (3, 4), 
	(4, 5), (5, 6), (6, 7), (7, 8), (8, 9), (9, 10)]
 
    # list of (min raised money, max raised money) -- ranges of raised money
    raised_pair_list = [(0, 1),
        (1, 400000),
        (400000, 10000000),
        (1000000, 1500000),
        (1500000, 2000000),
        (2000000, 2500000),
        (2500000, 3500000),
        (3500000, 5500000),
        (5500000, 8500000),
        (8500000, 12000000),
        (12000000, 20000000),
        (20000000, 30000000),
        (30000000, 50000000),
        (50000000, 100000000),
        (100000000, 1000000000),
        (1000000000, 1000000000000000)]
 
    stage_list = [
	'Series+A',
	'Series+B',
	'Acquired',
	'Series+C',
	'Series+D',
	'Seed',
	'IPO']

    def __init__(self):
        base_url = "https://angel.co/companies?stage=Seed" 
        driver = Driver.get_driver()
        dir_list = ["output", "code", 
	    "output/url_list_dir", "output/results_dir", 
	    "output/company_page_dir", "output/index_page_dir", 
	    "output/market_label_size_file_dir", "output/debug_dir"]
        market_label_file = 'market_labels.txt'
        locations = ['1688-United+States', '1624-California', 
	    '1664-New+York+City', '153509-Asia', '1642-Europe',
	    '1695-London,+GB', '1681-Silicon+Valley']

        scraper = AngelListScraper(base_url, driver)
        # above args are passed to scraper.start
        scraper.start(dir_list, market_label_file, 
            locations, signal_pair_list, 
            raised_pair_list, stage_list)
