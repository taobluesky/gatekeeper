function getOs()   
{   
   var OsObject = "";   
   if(navigator.userAgent.indexOf("MSIE")>0) {   
        return "MSIE";       //IE�����
   }
   if(isFirefox=navigator.userAgent.indexOf("Firefox")>0){   
        return "Firefox";     //Firefox�����
   }
   if(isSafari=navigator.userAgent.indexOf("Safari")>0) {   
        return "Safari";      //Safan�����
   }
   if(isCamino=navigator.userAgent.indexOf("Camino")>0){   
        return "Camino";   //Camino�����
   }
   if(isMozilla=navigator.userAgent.indexOf("Gecko/")>0){   
        return "Gecko";    //Gecko�����
   }   
} 

function xmlObj(){
	if (window.XMLHttpRequest){//��IE�������IE7(7.0�����ϰ汾)����xmlhttprequest���󴴽�
		xmlHttp = new XMLHttpRequest();
	}
	else if (window.ActiveXObject){//IE(6.0�����°汾)�������activexobject���󴴽�,����û������������ActiveX,���ܻ�ʧ��.
		xmlHttp = new ActiveXObject("Microsoft.XMLHTTP");
	}
	return xmlHttp;
}


