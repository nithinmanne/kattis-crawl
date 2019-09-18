import os
import sys
import mechanize
from bs4 import BeautifulSoup
import http.cookiejar
import urllib.request
import getpass


username = getpass.getuser()        # Change this to set custom username not email


if len(sys.argv) <= 1: output_path = input('Enter Output Location')
else: output_path = sys.argv[1]
output_path = os.path.abspath(output_path)

if os.path.exists(output_path):
    print(f'{output_path} Already Present! Exiting!')
    sys.exit(1)
elif not os.path.exists(os.path.dirname(output_path)):
    print(f'{os.path.dirname(output_path)} Not Present! Exiting!')
    sys.exit(1)

KATTIS_PAGE = 'https://uchicago.kattis.com'

LOGIN_PAGE = '/login'
PROBLEMS_PAGE = '/problems?show_solved=on&show_tried=off&show_untried=off'
PROBLEM_PAGE = '/problems/{problem}'

cookies = http.cookiejar.CookieJar()
browser = mechanize.Browser()
browser.set_handle_robots(False)
browser.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
browser.set_cookiejar(cookies)

browser.open(KATTIS_PAGE+LOGIN_PAGE)
browser.select_form(nr=1)
browser.form['user'] = username
browser.form['password'] = getpass.getpass()
browser.submit()

soup = BeautifulSoup(browser.open(KATTIS_PAGE+PROBLEMS_PAGE).read(), "html5lib")

problem_refs = soup.find_all('td', class_ = 'name_column')
problems = []
for problem in problem_refs: problems.append((problem.text, problem.contents[0]['href'][10:]))

HTML_TEMPLATE = '''<head>
  <meta http-equiv='refresh' content='0; URL={url}'>
</head>'''

os.chdir(os.path.dirname(output_path))
os.mkdir(os.path.basename(output_path))
os.chdir(os.path.basename(output_path))

for problem in problems:
    os.mkdir(problem[0])
    os.chdir(problem[0])
    with open(problem[1]+'.html', 'w') as html_file:
        html_file.write(HTML_TEMPLATE.format(url=KATTIS_PAGE+PROBLEM_PAGE.format(problem=problem[1])))
    os.chdir('..')