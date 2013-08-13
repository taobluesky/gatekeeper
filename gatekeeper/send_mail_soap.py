# -*- coding: utf-8 -*-

from suds.client import Client
url = 'http://msgcenter.ecmms.foxconn:2571/Messaging.asmx?WSDL'

client = Client(url)
header = client.factory.create('AuthenticationSoapHeader')
header.UserId = 'GateKeeperUid'
header.Password = 'GateKeeperPwd'
client.set_options(soapheaders=header)

#client.AuthenticationSoapHeaderValue = header
body = u'''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>Gatekeeper</title>
<style type="text/css">
body p {
	text-align: center;
}
</style>
</head>

<body>
<p>以下是HTML Table 代碼測試:</p>
<table width="313" border="1" align="center" cellpadding="1" cellspacing="0">
	<tr>
		<td width="102">頁面編碼使用:</td>
		<td width="105">UTF-8</td>
		<td width="84">&nbsp;</td>
	</tr>
	<tr>
		<td>&nbsp;</td>
		<td>我是简体字.</td>
		<td>&nbsp;</td>
	</tr>
	<tr>
		<td>&nbsp;</td>
		<td>我是繁體字</td>
		<td>english</td>
	</tr>
</table>
<p>以下是郵件內容:</p>
<p>TEST for 116 super notes!</p>
</body>
</html>
'''
subject=u"您在《Gate Keeper》 系統中申请已提交"
send_group_mail = client.service.SendGroupMails(
    To='ces-it-tech@mail.foxconn.com',
    Cc='',
    Subject=subject,
    Body=body,
    SmtpId='ces-it-tech@mail.foxconn.com',
    SmtpPassowrd='',
    SmtpAddress='ces-it-tech@mail.foxconn.com',
    NoteAddress='',
    NotesPassword='',
    )
    
print type(send_group_mail)
print send_group_mail