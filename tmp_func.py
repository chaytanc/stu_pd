# Target url becomes the url this returns if used a second time ?
def check_company_count(self, tmp_filter_list, target_url, url_list, ff, sf):
    company_count = self.get_company_count()
    if company_count > 400:
        log_time()
        # index page too long; dividing
        for filtr in tmp_filter_list:
            div_url = target_url + filtr
            new_company_count = self.get_company_count_on_search_page(
                target_url=div_url)

            self.url_generator_pause()

            self.make_company_dict(url_list, div_url, 
                new_company_count, ff, sf)

def make_company_dict(self, url_list, div_url, company_count, ff, sf):
    if company_count > 0:
        url_list.append(dict(url = div_url,
            fname = self.url_to_base_fname(div_url),
            company_count = company_count,
            featured = ff,
            signal = sf[1][1]))

    else:
        log_time()
        # Err not adding urls due to empty list

def make_market_labels_from_file(self, code_dir, market_label_file):
    if market_label_file is None:
        market_labels = []
    #XXX 
    #path_of_market_label_file = os.path.join(
        #code_dir, os.path.basename(market_label_file))
    else:
	with open(os.path.abspath(market_label_file), 'r') as f:
	    m = f.readlines()
	market_labels = [x.strip() for x in m]

    return market_labels

#XXX returned market_filters instead of self
def make_market_filters(self, market_labels)
    if market_labels and not self.skip_market_filter:
        #XXX what is happening here
        # Fills market_filters with each label and replaces spaces with +
        market_filters = ['&markets[]={}'.format
	    (x.replace(' ', '+')).replace('+++', '+')
	    for x in market_labels]
        market_filters.insert(0, '')
    return market_filters





