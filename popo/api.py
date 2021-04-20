import os
from ebooklib import epub
import requests
from selenium import webdriver
import time
from zhconv import convert
from selenium.webdriver.chrome.options import Options
prefs = {"profile.managed_default_content_settings.images":2}
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_experimental_option("prefs",prefs)
BookUrl = 'https://www.popo.tw/books/'
BookChapter = 'https://www.popo.tw/books/{}/articles'

class PoPo():
    def __init__(self,bookId,cookies):
        self._bookId = bookId
        self.urlList = []
        self.EpubList = []

        self._driver = webdriver.Chrome('./chromedriver.exe',options=chrome_options)
        self._driver.get('https://members.popo.tw/apps/login.php')
        for i in cookies:
            self._driver.add_cookie(cookie_dict=i)
    def getChapter(self):
        self._driver.get(BookChapter.format(self._bookId))
        if self.__isLimit18():
            self._driver.get(BookChapter.format(self._bookId))
        t = 0
        self._bookName = convert(self._driver.find_element_by_xpath('//*[@class="title"]').text,
                                 'zh-cn')
        self._authorName = convert(self._driver.find_element_by_xpath('//*[@class="b_author"]').text,
                                   'zh-cn').split('/')[0].strip()
        self.coverImgUrl = self._driver.find_element_by_xpath('//*[@id="rs"]').get_attribute('src')
        print(self._bookName,self._authorName)
        while True:

            for i in self._driver.find_elements_by_xpath('//*[@id="w0"]/div[*]/div'):
                if i.find_element_by_xpath('./a').get_attribute('class') == 'c4 BTN_pink':
                    break
                self.urlList.append(i.find_element_by_xpath('./div[2]/a').get_attribute('href'))
            try:
                if self._driver.find_element_by_xpath('//*[@id="w1"]/a[last()]').get_attribute('class') != 'num current':
                    # click to the next page.
                    self._driver.find_element_by_xpath('//*[@id="w1"]/a[last()-1]').click()
                    # print('yes')
                else:
                    break
            except:
                break


    def close(self):
        self._driver.close()

    def getText(self,url):
        self._driver.get(url)
        try:
            txt = convert(self._driver.find_element_by_xpath('//*[@id="readmask"]/div/h2').text, 'zh-cn')
        except:
            time.sleep(10)
            self._driver.get(url)
            txt = convert(self._driver.find_element_by_xpath('//*[@id="readmask"]/div/h2').text, 'zh-cn')
        epub = '<h1>' + txt + '</h1>'
        txt += '\n'
        t = self._driver.find_element_by_xpath('//*[@id="readmask"]/div')
        a = t.find_elements_by_css_selector('p')
        for i in a:
            txt +=  convert(i.text, 'zh-cn') + '\n'
            epub += '<p>' + convert(i.text, 'zh-cn') + '</p>'
        return txt, epub

    def __isLimit18(self):
        if self._driver.current_url.split('/')[-1] == 'limit18':
            self._driver.find_element_by_xpath('//*[@id="books-form"]/div/div/a[2]').click()
            return True
        else:
            return False

    def write2txt(self,txt):
        with open('./' + self._bookName + '({}).txt'.format(self._authorName), 'a', encoding='utf-8') as f:
            f.write(txt)
        return True
    def write2epub(self,epubList):
        if not os.path.exists('./temp'):
            os.mkdir('./temp')
        default_style = '''
        body {font-size:100%;}
        p{
            font-family: Auto;
            text-indent: 2em;
        }
        h1{
            font-style: normal;
            font-size: 20px;
            font-family: Auto;
        }      
        '''
        book = epub.EpubBook()
        book.set_identifier(self._bookId)
        book.set_title(self._bookName)
        book.set_language('zh-CN')
        book.add_author(self._authorName)
        imgb = requests.get(self.coverImgUrl)
        book.set_cover(self._bookName + '.png', imgb.content)
        default_css = epub.EpubItem(uid="style_default", file_name="style/default.css", media_type="text/css",
                                    content=default_style)
        book.add_item(default_css)
        u = 0
        for i in epubList:
            title = i.split('</h1>')[0]
            title = title.split('<h1>')[-1]
            print('\t'+title)
            c = epub.EpubHtml(title=title, file_name='chapter_{}'.format(u) +'.xhtml',lang = 'zh-CN',uid='chapter_{}'.format(u))
            c.content = i
            c.add_item(default_css)
            book.add_item(c)
            self.EpubList.append(c)
            u += 1
        book.toc = tuple(self.EpubList)
        book.spine = ['nav']
        book.spine.extend(self.EpubList)
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        style = '''
                body {
                    font-family: Auto;
                }
                p{
                     font-family: Auto;
                     text-indent: 2em;
                }
                h2 {
                     text-align: left;
                     text-transform: uppercase;
                     font-weight: 200;     
                }
                ol {
                        list-style-type: none;
                }
                ol > li:first-child {
                        margin-top: 0.3em;
                }
                nav[epub|type~='toc'] > ol > li > ol  {
                    list-style-type:square;
                }
                nav[epub|type~='toc'] > ol > li > ol > li {
                        margin-top: 0.3em;
                }
                '''
        nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
        book.add_item(nav_css)
        epub.write_epub('./' + self._bookName + '.epub', book, {})
    def run(self,bookId=''):
        if bookId != '':
            self._bookId = bookId
            self.urlList = []
            self.EpubList = []
        self.getChapter()
        List = []
        for i in self.urlList:
            txt, epub = self.getText(i)
            self.write2txt(txt)
            List.append(epub)
        self.write2epub(epubList=List)


