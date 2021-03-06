import os
import sys
import mechanize
from bs4 import BeautifulSoup
import http.cookiejar
import urllib.request
import getpass
import zipfile


username = getpass.getuser()        # Change this to set custom username not email


if len(sys.argv) <= 1: output_path = input('Enter Output Location: ')
else: output_path = sys.argv[1]
output_path = os.path.abspath(output_path)

if os.path.exists(output_path):
    print(f'{output_path} Already Present! Exiting!')
    sys.exit(1)
elif not os.path.exists(os.path.dirname(output_path)):
    print(f'{os.path.dirname(output_path)} Not Present! Exiting!')
    sys.exit(1)

KATTIS_PAGE = 'https://uchicago.kattis.com'
OPEN_KATTIS_PAGE = 'https://open.kattis.com'

LOGIN_PAGE = '/login'
PROBLEMS_PAGE = '/problems?show_solved=on&show_tried=off&show_untried=off'
PROBLEM_PAGE = '/problems/{problem}'
SAMPLES_PAGE = '/file/statement/'
SAMPLES_NAME = 'samples.zip'
SUBMISSIONS_PAGE = '/users/{username}/submissions/{problem}'
SUBMISSION_PAGE = '/submissions/{submission}/source/'
SUBMISSION_NAME = '{problem}.py'
README_NAME = 'README.md'

cookies = http.cookiejar.CookieJar()
browser = mechanize.Browser()
browser.set_handle_robots(False)
browser.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
browser.set_cookiejar(cookies)

browser.open(KATTIS_PAGE+LOGIN_PAGE)
browser.select_form(nr=1)
browser.form['user'] = username
print(f'Username: {username}')
browser.form['password'] = getpass.getpass()
browser.submit()

soup = BeautifulSoup(browser.open(KATTIS_PAGE+PROBLEMS_PAGE).read(), "html5lib")

problem_refs = soup.find_all('td', class_ = 'name_column')
problems = []
for problem in problem_refs: problems.append((problem.text, problem.contents[0]['href'][10:]))

os.chdir(os.path.dirname(output_path))
os.mkdir(os.path.basename(output_path))
os.chdir(os.path.basename(output_path))

HTML_TEMPLATE = '''<head>
  <meta http-equiv='refresh' content='0; URL={url}'>
</head>'''
README_TEMPLATE = '''# {problem_name}
URL: [{problem}]({url})'''

for problem in problems:
    dir_name = problem[0].replace('?', '_').replace('.', '_')
    os.mkdir(dir_name)
    os.chdir(dir_name)
    if 'uchicago' in problem[1]:
        url = KATTIS_PAGE+PROBLEM_PAGE.format(problem=problem[1])
    else:
        url = OPEN_KATTIS_PAGE+PROBLEM_PAGE.format(problem=problem[1])
    with open(problem[1]+'.html', 'w') as html_file:
        html_file.write(HTML_TEMPLATE.format(url=url))
    with open(README_NAME, 'w') as readme_file:
        readme_file.write(README_TEMPLATE.format(problem_name=problem[0], problem=problem[1], url=url))
    try:
        browser.retrieve(KATTIS_PAGE+PROBLEM_PAGE.format(problem=problem[1])+SAMPLES_PAGE+SAMPLES_NAME, SAMPLES_NAME)
        with zipfile.ZipFile(SAMPLES_NAME, 'r') as zipfile_ref:
            zipfile_ref.extractall(SAMPLES_NAME.split('.')[0])
        os.remove(SAMPLES_NAME)
    except:
        print(f'Warning! Samples for "{problem[0]}" Not Found')
    psoup = BeautifulSoup(browser.open(KATTIS_PAGE+SUBMISSIONS_PAGE.format(username=username, problem=problem[1])).read(), "html5lib")
    submission_refs = psoup.find_all('td', class_ = 'submission_id')
    submissions = []
    for submission in submission_refs:
        submissions.append(submission.text)
    for submission in sorted(submissions, key=int, reverse=True):
        submission_ref = psoup.find_all('tr', attrs={"data-submission-id":submission})[0]
        if submission_ref.contents[3].text != 'Accepted': continue
        browser.retrieve(KATTIS_PAGE+SUBMISSION_PAGE.format(submission=submission)+SUBMISSION_NAME.format(problem=problem[1].split('.')[-1]), SUBMISSION_NAME.format(problem=problem[1].split('.')[-1]))
        break
    os.chdir('..')