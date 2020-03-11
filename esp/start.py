from microWebSrv import MicroWebSrvimport wifi_utilsimport timeimport logginglogging.basicConfig(level=logging.INFO)log = logging.getLogger("start")# ----------------------------------------------------------------------------@MicroWebSrv.route('/')def _httpHandlerMainGet(httpClient, httpResponse):    ssid_list = wifi_utils.ssid_list    ssid_select = ""    time.sleep(3)    ifconfig = wifi_utils.get_ifconfig()    ip, net_mask, gateway, dns = ifconfig[0], ifconfig[1], ifconfig[2], ifconfig[3]    for ssid in wifi_utils.ssid_list:        ssid_select += '<option value="{0}">{0}</option>'.format(ssid.decode())    html = """\<!DOCTYPE html><html><head>	<title>Sensor Web Server</title>	<meta name="viewport" content="width=device-width, initial-scale=1"></head><body>  <div>Current IP: {1}</div>	<form action="/" method="post">	    <div>	        <label>Device Name</label>	        <input type="text" value="{3}" name="device_name">	    </div>		<div>			<label>Wifi Name</label>			<select name="ssid">				{0}			</select>		</div>		<div>			<label>Wifi Password</label>			<input type="password" placeholder="Enter Password" name="psw" required>		</div>		<div>			<label>MQTT Broker</label>			<input type="text" name="mqtt_broker" placeholder="MQTT broker server">		</div>		<div>			<label>Low Power Mode</label>			<input name="low_power_mode" placeholder="Low Power Mode True or False">		</div>		<div>			<label>Sensor Data Publish Interval</label>			<input name="publish_interval" value="30">		</div>		<button type="submit">Set Wifi</button>	</form></body></html>""".format(ssid_select, ip, wifi_utils.wifi_conf.get('device_name', "New Device"))    httpResponse.WriteResponseOk(headers=None,                                 contentType="text/html",                                 contentCharset="UTF-8",                                 content=html)@MicroWebSrv.route('/', 'POST')def __httpHandlerMainPost(httpClient, httpResponse):    formData = httpClient.ReadRequestPostedFormData()    log.info("form data: {0}".format(formData))    ssid = formData.get("ssid", None)    ssid_pass = formData.get("psw", None)    mqtt_broker = formData.get("mqtt_broker", None)    low_power_mode = formData.get("low_power_mode", None)    publish_interval = formData.get("publish_interval", None)    device_name = formData.get("device_name", "New Device")    wifi_utils.save_setting(ssid, ssid_pass, mqtt_broker, low_power_mode, publish_interval, device_name)    if ssid and ssid_pass:        wifi_utils.connect_wifi(ssid, ssid_pass)    content = """\  <!DOCTYPE html>  <html>    <head>      <meta charset="UTF-8">        <title>Setting saved</title>        <body>Setting saved</body>    </head>  </html>  """    httpResponse.WriteResponseOk(headers=None,                                 contentType="text/html",                                 contentCharset="UTF-8",                                 content=content)@MicroWebSrv.route('/test')def _httpHandlerTestGet(httpClient, httpResponse):    content = """\	<!DOCTYPE html>	<html lang=en>        <head>        	<meta charset="UTF-8" />            <title>TEST GET</title>        </head>        <body>            <h1>TEST GET</h1>            Client IP address = %s            <br />			<form action="/test" method="post" accept-charset="ISO-8859-1">				First name: <input type="text" name="firstname"><br />				Last name: <input type="text" name="lastname"><br />				<input type="submit" value="Submit">			</form>        </body>    </html>	""" % httpClient.GetIPAddr()    httpResponse.WriteResponseOk(headers=None,                                 contentType="text/html",                                 contentCharset="UTF-8",                                 content=content)@MicroWebSrv.route('/test', 'POST')def _httpHandlerTestPost(httpClient, httpResponse):    formData = httpClient.ReadRequestPostedFormData()    firstname = formData["firstname"]    lastname = formData["lastname"]    content = """\	<!DOCTYPE html>	<html lang=en>		<head>			<meta charset="UTF-8" />            <title>TEST POST</title>        </head>        <body>            <h1>TEST POST</h1>            Firstname = %s<br />            Lastname = %s<br />        </body>    </html>	""" % (MicroWebSrv.HTMLEscape(firstname),           MicroWebSrv.HTMLEscape(lastname))    httpResponse.WriteResponseOk(headers=None,                                 contentType="text/html",                                 contentCharset="UTF-8",                                 content=content)@MicroWebSrv.route('/edit/<index>')  # <IP>/edit/123           ->   args['index']=123@MicroWebSrv.route('/edit/<index>/abc/<foo>')  # <IP>/edit/123/abc/bar   ->   args['index']=123  args['foo']='bar'@MicroWebSrv.route('/edit')  # <IP>/edit               ->   args={}def _httpHandlerEditWithArgs(httpClient, httpResponse, args={}):    content = """\	<!DOCTYPE html>	<html lang=en>        <head>        	<meta charset="UTF-8" />            <title>TEST EDIT</title>        </head>        <body>	"""    content += "<h1>EDIT item with {} variable arguments</h1>".format(len(args))    if 'index' in args:        content += "<p>index = {}</p>".format(args['index'])    if 'foo' in args:        content += "<p>foo = {}</p>".format(args['foo'])    content += """        </body>    </html>	"""    httpResponse.WriteResponseOk(headers=None,                                 contentType="text/html",                                 contentCharset="UTF-8",                                 content=content)# ----------------------------------------------------------------------------def _acceptWebSocketCallback(webSocket, httpClient):    print("WS ACCEPT")    webSocket.RecvTextCallback = _recvTextCallback    webSocket.RecvBinaryCallback = _recvBinaryCallback    webSocket.ClosedCallback = _closedCallbackdef _recvTextCallback(webSocket, msg):    print("WS RECV TEXT : %s" % msg)    webSocket.SendText("Reply for %s" % msg)def _recvBinaryCallback(webSocket, data):    print("WS RECV DATA : %s" % data)def _closedCallback(webSocket):    print("WS CLOSED")# ----------------------------------------------------------------------------# routeHandlers = [#	( "/test",	"GET",	_httpHandlerTestGet ),#	( "/test",	"POST",	_httpHandlerTestPost )# ]def start_webserver():    srv = MicroWebSrv(webPath='www/')    srv.MaxWebSocketRecvLen = 256    srv.WebSocketThreaded = True    srv.AcceptWebSocketCallback = _acceptWebSocketCallback    srv.Start(threaded=True)# ----------------------------------------------------------------------------