#-*-coding:utf-8-*-
import copy

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
from reportlab.platypus import *
from reportlab.lib import colors
from reportlab.lib import pdfencrypt
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.lib.enums import TA_CENTER

from reportlab.graphics.barcode.code128 import *
from reportlab.graphics.barcode import createBarcodeDrawing

pageinfo = "gatekeeper"

def _register_zhfont():
    """ 中文字體處理
    """
    #pdfmetrics.registerFont(UnicodeCIDFont('MSung-Light'))
    #pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
    pdfmetrics.registerFont(TTFont('msjh', 'c:/msjh.ttf'))
    pdfmetrics.registerFont(TTFont('msjhbd', 'c:/msjhbd.ttf'))
    registerFontFamily('yahei',normal='msjh',bold='msjhbd',italic='msjh',boldItalic='msjhbd')
    
def gen_carry_pdf(filename='out.pdf',data={}):
    """ 生成攜入攜出申請單PDF檔案
    """
    _register_zhfont()
    # Our container for 'Flowable' objects
    elements = []
    # A large collection of style sheets pre-made for us
    styles = getSampleStyleSheet()
    # 使用StandardEncryption加密PDF檔案
    enc = pdfencrypt.StandardEncryption(userPassword='',
        canPrint=1,
        canModify=0,
        canCopy=0,
        canAnnotate=0,
        strength=40
    )
    # A basic document for us to write to pdf
    doc = SimpleDocTemplate(filename,encrypt=enc)
    # 添加文檔標題
    elements.append(Paragraph(u"<font name='yahei'>富士康科技集團（天津園區）<br/>資訊設備攜入攜出放行單</font>",
                    styles['Title']))
    btstyle = copy.deepcopy(styles['BodyText'])
    btstyle.wordWrap = True
    p1 = Paragraph(u"<font name='yahei' size='16'>簽名處(攜入確認):<br/></font>",styles['BodyText'])
    p2 = Paragraph(u"<font name='yahei' size='16'>簽名處(攜出確認):<br/></font>",styles['BodyText'])
    p3 = Paragraph(u"<font name='yahei' size='10'>%s</font>"% data.get('department'),
       styles['BodyText'])
    s = [p1,Spacer(36, 75)]
    s1 =[p2,Spacer(36, 75)]
    # 創建Code128條形碼
    barcode_value = data.get('app_no','')
    code = createBarcodeDrawing("Code128", humanReadable=1,value=barcode_value)#,**options
    code.renderScale = 1.0
    # 創建 table data
    td = [
            [u'攜帶人/接待人信息'],
            [u'姓名',data.get('name')],
            [u'工號',data.get('emp_no')],
            [u'部門',p3],#data.get('department')
            [u'設備信息'],
            [u'品牌',  data.get('manufacturer')],
            [u'型號',  data.get('model_no')],
            [u'顏色',  data.get('color')],
            [u'序號',  data.get('sn')],
            [u'核對以上信息，并確認下面信息！！'],
            [u'單號',  code],
            [u'攜入日期',  data.get('in_date','-')],
            [u'攜出日期',  data.get('out_date','-')],
            [u'攜出目的地',data.get('out_dest','-')],
            [u'門崗簽名',],
            [s,s1]
            ]
    # 設置table style
    ts = [
    # 表格行樣式
         ('ALIGN', (0,0), (-1,-1), 'LEFT'),
         ('LINEABOVE', (0,0), (-1,0), 1, colors.purple),
         ('LINEBELOW', (0,0), (-1,0), 1, colors.purple),
         ('LINEABOVE', (0,4), (-1,4), 1, colors.purple),
         ('LINEBELOW', (0,4), (-1,4), 1, colors.purple),
         ('LINEABOVE', (0,9), (-1,9), 1, colors.purple),
         ('LINEBELOW', (0,9), (-1,9), 1, colors.purple),
         ('LINEABOVE', (0,-2), (-1,-2), 1, colors.purple),
         ('LINEBELOW', (0,-2), (-1,-2), 1, colors.purple),
         ('LINEBELOW', (0,-1), (-1,-1), 2, colors.purple),
         ('BOX', (0,0), (-1,-1), 2, colors.purple),
         
         ('BACKGROUND',(0,0),(0,0),colors.HexColor('#d1b2ff')),
         ('BACKGROUND',(0,4),(0,4),colors.HexColor('#d1b2ff')),
         ('BACKGROUND',(0,9),(0,9),colors.HexColor('#d1b2ff')),
         ('BACKGROUND',(0,-2),(0,-2),colors.HexColor('#d1b2ff')),
         
         ('FONT', (0,0), (-1,-1), 'msjh'),
         ('FONTSIZE', (0,0), (-1,-1), 16),
    # 單元格間距,行距,垂直對齊方式
         #('LEFTPADDING', (0,0), (-1,-1), 10),
         #('RIGHTPADDING', (0,0), (-1,-1), 10),
         #('BOTTOMPADDING', (0,0), (-1,-1), 6),
         #('TOPPADDING', (0,0), (-1,-1), 6),
         ('LEADING', (0,0), (-1,-1), 20),
         ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    # 合併單元格
         ('SPAN',(0,0),(1,0)),
         ('SPAN',(0,4),(1,4)),
         ('SPAN',(0,9),(1,9)),
         #('SPAN',(0,-3),(1,-3)),
         ('SPAN',(0,-2),(1,-2)),
         ]

    table = Table(td, colWidths=[3*inch,4*inch],style=ts)
    #table._argW[0]=3*inch
    #table._argW[1]=4*inch
    elements.append(Spacer(1,0.5*inch))
    elements.append(table)
    # Write the document to disk
    doc.build(elements,onFirstPage=myFirstPage, onLaterPages=myLaterPages)

def myFirstPage(canvas, doc):
    PAGE_HEIGHT=defaultPageSize[1]; PAGE_WIDTH=defaultPageSize[0]
    canvas.saveState()
    #canvas.setFont('Times-Bold',16)
    #canvas.drawCentredString(PAGE_WIDTH/2.0, PAGE_HEIGHT-108, Title)
    canvas.setFont('Times-Roman',9)
    canvas.drawString(inch, 0.75 * inch, "Page 1/ %s" % pageinfo)
    canvas.restoreState()
    
def myLaterPages(canvas, doc):
    canvas.saveState()
    canvas.setFont('Times-Roman',9)
    canvas.drawString(inch, 0.75 * inch, "Page %d %s" % (doc.page, pageinfo))
    canvas.restoreState()

if __name__=='__main__':
    data ={'name':u'李崽崽',
        'department':u'(天津)IT/SSDC/天津資訊整合服務部/辦公運維服務課',
        'emp_no':'H710494X',
        'manufacturer':u'APPLE',
        'model_no':u'MC966CH/A',
        'sn':u'XXXX-HHHHH-YYYYYY',
        'color':u'白色',
        'app_no':'TJCARRY130711000113C6',
        'in_date':'2013-06-01',
        'out_date':'2013-06-05',
        'out_dest':u'天富7號樓',
        'bar_code':'TJCARRY-TEST-111',
    }
    #data['department']=u'(天津)EPD(V) 沖件開發處/客制彈性量產制造廠--供應鏈管理課'
    gen_carry_pdf(filename='test.pdf',data=data)
