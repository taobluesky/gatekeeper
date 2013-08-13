function getOs()   
{   
   var OsObject = "";   
   if(navigator.userAgent.indexOf("MSIE")>0) {   
        return "MSIE";       //IE浏览器
   }
   if(isFirefox=navigator.userAgent.indexOf("Firefox")>0){   
        return "Firefox";     //Firefox浏览器
   }
   if(isSafari=navigator.userAgent.indexOf("Safari")>0) {   
        return "Safari";      //Safan浏览器
   }
   if(isCamino=navigator.userAgent.indexOf("Camino")>0){   
        return "Camino";   //Camino浏览器
   }
   if(isMozilla=navigator.userAgent.indexOf("Gecko/")>0){   
        return "Gecko";    //Gecko浏览器
   }   
} 

function xmlObj(){
	if (window.XMLHttpRequest){//非IE浏览器及IE7(7.0及以上版本)，用xmlhttprequest对象创建
		xmlHttp = new XMLHttpRequest();
	}
	else if (window.ActiveXObject){//IE(6.0及以下版本)浏览器用activexobject对象创建,如果用户浏览器禁用了ActiveX,可能会失败.
		xmlHttp = new ActiveXObject("Microsoft.XMLHTTP");
	}
	return xmlHttp;
}


