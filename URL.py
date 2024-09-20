import socket
import ssl

class URL:
    def __init__(self, url):
        try:
            self.scheme, url = url.split("://", 1)
            assert self.scheme in ["http", "https"]
            if "/" not in url:
                url += "/"
            self.host, url = url.split("/", 1)
            self.path = "/" + url
            self.connection = "1.1"

        except Exception as e:
            self.host = ""
            self.path = "about:blank"
            self.connection = "1.1"
            self.scheme = "http"

    def request(self):
        if self.path == "about:blank":
            return ""

        # create socket
        s = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP,
        )

        if ":" in self.host:
            self.host, port = self.host.split(":", 1)
            self.port = int(port)

        # connect to host change port based on scheme
        if self.scheme == "http":
            self.port = 80

        elif self.scheme == "https":
            self.port = 443
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname=self.host)

        s.connect((self.host, self.port))

        # send data of request
        request = "GET {} HTTP/1.0\r\n".format(self.path)
        request += "Host: {}\r\n".format(self.host)
        request += "Connection: {}\r\n".format(self.connection)
        request += "\r\n"
        s.send(request.encode("utf8"))

        # read response
        response = s.makefile("r", encoding="utf8", newline="\r\n")
        statusline = response.readline()
        version, status, explanation = statusline.split(" ", 2)

        headers = {}

        while True:
            line = response.readline()
            if line == "\r\n":
                break

            header, value = line.split(":", 1)
            headers[header.casefold()] = value.strip()

        assert "transfer-encoding" not in headers
        assert "content-encoding" not in headers
        content = response.read()
        s.close()
        return content