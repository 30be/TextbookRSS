import sys
from bs4 import BeautifulSoup

html_content = sys.stdin.read()
soup = BeautifulSoup(html_content, "html.parser")
links = [a["href"] for a in soup.find_all("a", href=True)]
for link in links:
    print(link)
