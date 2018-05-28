from bs4 import BeautifulSoup
import urllib
import requests

html = urllib.urlopen=('http://gall.dcinside.com/board/lists/?id=idolmaster')
soup = BeautifulSoup(html, "lxml")

link = soup.find_all("td", { "class" : "t_subject" })\

for m in link:
    if(m.find("a", {"class" : "icon_notice"})):
        pass
    else:
        print(m.a.string)
