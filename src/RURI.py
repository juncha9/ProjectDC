from collections import Counter
import pandas as pd
import pytagcloud
import urllib
import requests
from konlpy.tag import Twitter
from bs4 import BeautifulSoup
from tkinter import Tk,Label,OptionMenu,StringVar,IntVar,PhotoImage,Button
import os.path
import sys
import time

def GetHtml(url):
   _html = ""
   resp = requests.get(url) #requests모듈을 이용 응답하는 컨텐츠를 가져옴
   if resp.status_code == 200:
      _html = resp.text
   return _html

def DrawCloud(tags, filename, fontname='Nanum Gothic Coding', size=(2000, 2000), rectangular=True):
    pytagcloud.create_tag_image(tags, filename, fontname=fontname, size=size, rectangular=rectangular)

def DelOneChar(nouns):
    count = 0
    delCount = 0
    for s in nouns:
        if (len(s) == 1):
            nouns[count] = 'del'
            delCount += 1
        count +=1
    for i in range(0,delCount):
        nouns.remove('del')
    return nouns

def DFIndexing(DataFrame,DFid,DFidColName,findColName): #0번째 행의 id를 참조하여 원하는 행의 데이터한개를 리턴
    ret = str(DataFrame.loc[DataFrame[DFidColName] == DFid,findColName].values[0])
    return ret

#루리웹 게시판 구조
# <tr class="table_body">
#   <td class="id"> 아이디 *
#   <a href= ~~~ > 게시물명 *
#   <td class="time"> 시간  *
# </tr>

def WordListToCounter(wordList):
    twitter = Twitter()
    c = 1
    data = str()
    count = Counter() # count변수에 {단어:횟수} 배열이 들어갈것
    #초기화

    print("Start data to word count")
    for title in wordList: #data변수에 크롤링한 제목들을 한줄로 만듬
        if (c<=1):
            print("Read 1000 data ... ",end="")
        data += str(title)
        data +="\n"
        if (c>1000):  #방대한 데이터이기 변수가 너무커지면 프로그램이 종료된다 때문에 반복문으로 처리하고 count변수만 증가시키기로 한다.
            c=0                     #1000개 도달
            nouns = twitter.nouns(data) #Twitter엔진에서 data를 가져와서 단어별로 추출하여 nouns변수에 저장 
                                        #nouns는 대입연산자로 초기화되기 때문에 따로 초기화가 필요없음
            nouns = DelOneChar(nouns) #nouns에서 한글자를 제거
            count += Counter(nouns)     #count변수는 계속 증가시킬것이므로 합산처리
            data = str()             #data 초기화
            print("done",end="\n")
        c += 1
    nouns = twitter.nouns(data)
    nouns = DelOneChar(nouns) #nouns에서 한글자를 제거
    count += Counter(nouns)
    data = str()
    print("end",end="\n")
    print("Success to create Counter",end="\n")
    return count

def CounterToCloudTags(count, topCount, defMinSize = 28, defMaxSize = 300):
        diff = (40 - int(len(count) / count.most_common(1)[0][1]))
        print('Diff (40 - WordKinds / HotKeyCount): '+str(diff))
        #if ( diff<=0 ):
         #   diff = 0
        maxSizeAdd = int(diff)
        minSizeAdd = int(diff)
        print("Start top("+str(topCount)+') word to cloud tags, maxSize: '+str(defMaxSize)+'+'+str(maxSizeAdd)+' minSize: '+str(defMinSize)+'+'+str(minSizeAdd))
        tags = count.most_common(topCount)
        cloudTags = pytagcloud.make_tags(tags, minsize=defMinSize+minSizeAdd, maxsize=(defMaxSize+maxSizeAdd))
        print('Success to create CloudTags')
        return cloudTags

def PageToCloud(path,link,endPage=100):
    colname = ['title']
    wordDF = pd.DataFrame(columns=colname) #크롤링 정보를 담을 데이터프레임
    startPage = 1
    pages = range(startPage,endPage)
    count = 1 
    print("Crawl start (page:"+str(startPage)+"~"+str(endPage)+")")
    for i in pages:
        URL  = 'http://bbs.ruliweb.com/'+link+'/list?page='+str(i)
        html = GetHtml(URL)
        soup = BeautifulSoup(html, "lxml") #BeatifulSoup을 이용해 정리 soup에 정리된 결과 저장됨
        bodyContents = soup.find_all("tr", { "class" : "table_body" })
        print("page "+str(count)+" reading ... ",end='')
        for content in bodyContents:
            if( content.find("a", {"class":"deco"}) ):
                if(content.find_all("strong") ):
                    continue  
                title = str(content.find("a",{"class":"deco"}).string).strip()
                wordDF = wordDF.append({'title':title},ignore_index=True)
        count += 1
        print("done",end='\n')
    print("Success to Crawl")

    #초기화
    wordList = wordDF['title']

    print('Create Counter')
    count = WordListToCounter(wordList)
    print('Hot keyword: '+str(count.most_common(1)[0])+'  Word kinds: '+str(len(count))) #40

    topWordCount = 200 #상위 단어 수
    print('Create CloudTags')
    cloudTags = CounterToCloudTags(count,topWordCount,30,300)
    print('Create Cloud')
    DrawCloud(cloudTags, path)
    print('Success to create Cloud (path:'+path+')')


def PageToCSV(path,link,endPage=100):
    colname = ['bid','assort','title','writer', 'suggest','hit','time','link']
    df = pd.DataFrame(columns=colname) #크롤링 정보를 담을 데이터프레임
    startPage = 1
    pages = range(startPage,endPage)
    count = 1 
    print("Crawl start (page:"+str(startPage)+"~"+str(endPage)+")")
    for i in pages:
        
        URL  = 'http://bbs.ruliweb.com/'+link+'/list?page='+str(i)
        html = GetHtml(URL)
        soup = BeautifulSoup(html, "lxml") #BeatifulSoup을 이용해 정리 soup에 정리된 결과 저장됨
        bodyContents = soup.find_all("tr", { "class" : "table_body" })
        print("page "+str(count)+" reading ... ",end='')
        for content in bodyContents:
            if( content.find("a", {"class":"deco"}) ):
                if(content.find_all("strong") ):
                    continue
                bid = int(content.find("td",{"class":"id"}).string)
                assort = str(content.find("td",{"class":"divsn"}).find("a","").string).strip()
                title = str(content.find("a",{"class":"deco"}).string).strip()
                writer = str(content.find("td",{"class":"writer text_over"}).find("a","").string).strip()
                suggest = int(content.find("td",{"class":"recomd"}).string)
                hit = int(content.find("td",{"class":"hit"}).string)
                time = str(content.find("td",{"class":"time"}).string).strip()
                hyperlink = content.find("a",{"class":"deco"})['href']
                df = df.append({'bid':bid, 'assort':assort ,'title':title,'writer':writer,'suggest':suggest,'hit':hit,'time':time,'link': hyperlink } , ignore_index=True)
        count += 1
        print("done",end='\n')
    df.to_csv(path,mode='w',encoding='utf-8')
    print("Success to create CSV (path:"+path+')')

def CSVToCloud(CSVPath, cloudPath):
    if (not os.path.isfile(CSVPath)):
        print('error : ['+CSVPath+'] is not exist')
        return
    df = pd.read_csv(CSVPath,encoding='utf-8')
    wordList =  df['title']
    print("Reading CSV success")

    print('Create Counter')
    count = WordListToCounter(wordList)
    print('Hot keyword: '+str(count.most_common(1)[0])+'  Word kinds: '+str(len(count))) #40

    topWordCount = 200 #상위 단어 수
    print('Create CloudTags')
    cloudTags = CounterToCloudTags(count,topWordCount)
    print('Create Cloud')
    DrawCloud(cloudTags, cloudPath)
    print('Success to create Cloud (path:'+cloudPath+')')



#프로그램 시작
BoardIndexPath = 'Data\\BoardList.xlsx'
if (not os.path.isfile(BoardIndexPath)):
        print('error : ['+BoardIndexPath+'] is not exist')
        sys.exit(1)
#게시판 리스트
boardDF = pd.read_excel(BoardIndexPath,index=False)
print('Reading ['+BoardIndexPath+'] success',end='\n\n')
print(boardDF,end="\n\n")

#페이지수 범위
searchPageNumList = [10,50,100,200,300,400]

# **윈도우 초기화**
window = Tk()

# none 이미지 로딩
noneImgPath = 'Data\\None.png'
wordImage=PhotoImage(file=noneImgPath).subsample(x = 3)
if (not os.path.isfile(noneImgPath)):
        print('error : ['+noneImgPath+'] is not exist')
        sys.exit(1)
print('Reading ['+noneImgPath+'] success')

#윈도우 창 설정
window.title("Ruliweb.com Crawler")
window.geometry("670x785")

#드랍다운 메뉴 변수설정
boards = StringVar(window)
boards.set(boardDF['boardName'].values[0])
searchPageNum = IntVar(window)
searchPageNum.set(searchPageNumList[0])

#첫번째줄
boardLabel = Label(window,text='Made by juncha9, kimssi1992, tkwkajtls1')
boardLabel.config(width="92",height="1",anchor="e")
boardLabel.grid(row=0,column=0, columnspan=4 ,padx=2,pady=2)

#두번째줄 (드랍다운)
boardLabel = Label(window,text='Board Name')
boardLabel.config(width="10",height="1")
boardLabel.grid(row=1,column=0, padx=5 ,pady=5)
boardDropDown = OptionMenu(window,boards,*boardDF['boardName'] )
boardDropDown.config(width="24",height="1")
boardDropDown.grid(row=1,column=1, padx=5 ,pady=5)

pageLabel = Label(window,text='Search Pages')
pageLabel.config(width="10",height="1")
pageLabel.grid(row=1,column=2, padx=5 ,pady=5)
pagesDropDown = OptionMenu(window,searchPageNum,* searchPageNumList)
pagesDropDown.config(width="24",height="1")
pagesDropDown.grid(row=1,column=3, padx=5 ,pady=5)

#빈 이미지 로딩
imageLabel = Label(window,image=wordImage)
imageLabel.grid(row=3,pady=10,columnspan=4)

#세번째줄 (버튼들)
def pageToCloudRun():
    selectBoard = boards.get()
    selectPageN = searchPageNum.get()
    print('Board: '+selectBoard +' SearchPages: '+ str(selectPageN) )
    imagePath = 'Resources\\img\\'+DFIndexing(boardDF, selectBoard,'boardName','fileName')+'.png'
    PageToCloud(imagePath,DFIndexing(boardDF, selectBoard,'boardName','link'),selectPageN)
    if (os.path.isfile(imagePath)):
        print('['+imagePath+'] is exist. open it')
        newImage= PhotoImage(file=imagePath).subsample(x = 3)
        imageLabel.configure(image = newImage)
        imageLabel.image = newImage
        window.update()
    else:
        print('['+imagePath+'] is not exist. Something wrong')
    print("PageToCloud end")

pageToCloudButton = Button(window, text="Word Cloud Create",command=pageToCloudRun)
pageToCloudButton.config(width="43",height="1")
pageToCloudButton.grid(row=2,column=0,padx=5 ,pady=5, columnspan=2)

def pageToCSVRun():
    selectBoard = boards.get()
    selectPageN = searchPageNum.get()
    print('Board: '+selectBoard +' SearchPages: '+ str(selectPageN) )
    CSVPath = 'Resources\\csv\\'+DFIndexing(boardDF, selectBoard,'boardName','fileName')+'.csv'
    PageToCSV(CSVPath,DFIndexing(boardDF, selectBoard,'boardName','link'),selectPageN)
    print("PageToCSV end")
pageToCSVButton = Button(window, text="CSV Create", command=pageToCSVRun)
pageToCSVButton.config(width="43",height="1")
pageToCSVButton.grid(row=2,column=2, padx=5 ,pady=5, columnspan=2)

#윈도우 시작
window.mainloop()



