#-*-coding:utf-8-*-
import reportlab
import os

from reportlab.pdfgen import canvas
from reportlab.lib import pdfencrypt
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize

#reportlab.pdfbase.pdfmetrics.registerFont(reportlab.pdfbase.ttfonts.TTFont('song', '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'))

#中文字體處理
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
pdfmetrics.registerFont(UnicodeCIDFont('MSung-Light'))
pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
pdfmetrics.registerFont(TTFont('msjh', 'c:/msjh.ttf'))
pdfmetrics.registerFont(TTFont('msjhbd', 'c:/msjhbd.ttf'))

registerFontFamily('yahei',normal='msjh',bold='msjhbd',italic='msjh',boldItalic='msjhbd')

#配置PDF檔權限
enc=pdfencrypt.StandardEncryption(userPassword='',
    canPrint=1,
    canModify=0,
    canCopy=0,
    canAnnotate=0,
    strength=40
)
c = canvas.Canvas("p.pdf",encrypt=enc)

textobject = c.beginText()
#textobject.setCharSpace(charspace)
#textobject.setWordSpace(wordspace)
textobject.setTextOrigin(2*inch, 10*inch)
textobject.setFont('MSung-Light', 30)
#for line in lyrics:
#textobject.textLine(u"攜入/攜出放行單")
#textobject.setFillGray(0.4)
#textobject.textLines('''''')
c.drawText(textobject)

c.setFont('MSung-Light', 16)
# the two unicode characters below are "Tokyo"
msg = u'中文輸入'
c.drawString(100, 675, msg)
c.setFont('STSong-Light',16)
c.drawString(100, 600, msg)
c.setFont('msjh',16)
c.drawString(100, 550, msg)
c.setFont('msjhbd',16)
c.drawString(100, 500, msg)
#c.drawString(100, 100, u"Hello world.")
#c.drawString(0, 0, u"Hello world.")


c.setFont('msjhbd',16)
PAGE_HEIGHT=defaultPageSize[1]; PAGE_WIDTH=defaultPageSize[0]
c.drawCentredString(PAGE_WIDTH/2.0, PAGE_HEIGHT-108, u"攜入/攜出放行單")


c.showPage()
c.save()
'''
from reportlab.lib.styles import getSampleStyleSheet
stylesheet=getSampleStyleSheet()
import copy
normalStyle = copy.deepcopy(stylesheet['Normal'])
normalStyle.fontName ="MSung-Light"
normalStyle.fontSize = 20
story = []
story.append(Paragraph(u"<b>你好</b>,你好,中文", normalStyle))

doc = SimpleDocTemplate("p.pdf")
doc.build(story)
'''
