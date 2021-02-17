import json
import Main
from http.server import BaseHTTPRequestHandler, HTTPServer


hostName = "localhost"
serverPort = 8080

class MyServer(BaseHTTPRequestHandler):

    def do_POST(self):
        content_len = int(self.headers.get('Content-Length'))
        json_path = self.rfile.read(content_len)

        output, status_code = self.handle_json(json_path)
        if status_code == 200:
            out_json = json.dumps(output)

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(bytes(out_json, "utf-8"))
        else:
            msg = None
            if status_code == 401:
                 msg = 'None terrain dataset for given area feature'
            elif status_code == 402:
                msg = 'Invalid sampling distance'
            elif status_code == 403:
                msg = 'Invalid output units'
            elif status_code == 404:
                msg = 'Invalid area geometry'

            self.send_error(status_code,msg)


    def handle_json(self, json_path):
        json_output, status_code = Main.main(json_path)
        return json_output, status_code



if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")

