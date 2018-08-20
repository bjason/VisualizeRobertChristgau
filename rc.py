from bs4 import BeautifulSoup
from pyecharts import Bar
from pyecharts import Pie
import requests
import xlwt

rankList = ['A+','A','A-','B+','***','**','*','S','N','B','B-','C+','C',
            'C-','D+','D','D-','E+','E','E-','X']
rankTotal = []
rankAlbumTotal = []

for rank in rankList:
  print
  print rank
  print
  
  param = {'g': rank}
  retry = 50
  while retry > 0:
    print 'retrying: ' + str(retry)
    try:
      req = requests.get("https://www.robertchristgau.com/get_gl.php",
                       params = param, timeout = 5)
    except BaseException,e:
      print 'Timeout, try again'
      retry -= 1
    else:
      # succeed
      print 'ok'
      break
  else:
      # fail
      print 'Try 50 times, But all failed'

  #print req
  html = req.text
  soup = BeautifulSoup(html, 'html5lib')
  soup.prettify().encode("gbk", 'ignore').decode("gbk", "ignore")

  numPerYear = []
  numPerYearSoundTrack = []

  ul = soup.find_all('ul')

  #ordinary album list
  for item in ul[0].children:
    try:
      a = item.find_all('a')
      
      artist = a[0].string
      if len(a) > 1:
        album = a[1].string        
      else:
        album = item.i.string
        
      year = item.b.next_sibling.next_sibling.next_sibling.string[2:6]

      #print artist + ' - ' + album + ' (' + year + ')'

      numPerYear.append(int(year))
    except BaseException,e:
      continue

  print '\nCompilations/Soundtracks\n'

  #soundtrack list
  earliest = 0
  if len(ul) > 1:
    for item in ul[1].children:      
      try:
        album = item.a.string
      except BaseException,e:
        try:          
          album = item.i.string
        except BaseException,e:
          continue

      year = item.b.next_sibling.string[2:6]
      #print album + ' (' + year + ')'

      numPerYearSoundTrack.append(int(year))

    earliest = min(min(numPerYear), min(numPerYearSoundTrack))
    years = range(earliest,
                max(max(numPerYear), max(numPerYearSoundTrack)) + 1)
  else:
    earliest = min(numPerYear)
    years = range(earliest, max(numPerYear) + 1)

  c = []
  cs = []

  print earliest

  for year in years:
    c.append(numPerYear.count(year))
    cs.append(numPerYearSoundTrack.count(year))

  total = (sum(c) + sum(cs))
  rankTotal.append(total)
  rankAlbumTotal.append(sum(c))

  print total

  #rank-year data
  bar = Bar(rank + ' albums in year', 'albums: ' + str(sum(c)) +
            ' / total: ' + str(total))
  bar.add('album', years, c, is_stack=True)
  bar.add('compilations/soundtrack', years, cs, is_stack=True)
  bar.render(path=rank.replace('*', 'Star') + '.png')

pie = Pie('All Rank Statistic')
pie.add('total', rankList, rankTotal, center=[25, 50], is_random=True,
        radius=[30, 75], rosetype='radius')
pie.add('without soundtrack', rankList, rankAlbumTotal, center=[75, 50], is_random=True,
        radius=[30, 75], rosetype='radius')
pie.render(path='All rank statistic.png')
