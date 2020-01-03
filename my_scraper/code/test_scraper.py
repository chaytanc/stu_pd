import bs4
import pytest

html_doc = '<html>' \
           '<body>' \
           '  <div>No</div>' \
           '  <div class="results">' \
           '    <div data-_tn="companies/row">Yes</div>' \
           '  </div>' \
           '</body>' \
           '</html>'
soup = BeautifulSoup(html_doc, 'html.parser')

result = soup.find('div', attrs={'class': 'results'})
print(result)

result = soup(class_='results')[0]
print(result)
