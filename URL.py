import socket
import ssl
<<<<<<< HEAD

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
=======
import gzip

from checkEntity import checkEntity
#needs caching

class URL:
    def __init__(self, url) -> None:
        self.schemes = {
            "view-source": ":",
            "about:blank": ":",
            "http": "://",
            "https": "://",
            "file": "://",
            "data:text/html": ",",
        }
        
        self.url = url
        self.parse_url(url)
        self.connection = "close"  # add keep-alive

    def parse_url(self, url):
        # separate scheme from url
        for scheme in self.schemes:
            if scheme in url:
                if scheme == "view-source":
                    self.tag = "view-source"
                    url = url.split(self.schemes[scheme], 1)[1]
                else:
                    self.scheme, url = url.split(self.schemes[scheme], 1)
                    break

        if "/" not in url:
            url += "/"

        # separate host and path from url
        self.host, url = url.split("/", 1)

        # allows to access via different ports
        if not "C:" in self.host:
            if ":" in self.host:
                self.host, port = self.host.split(":", 1)
                self.port = int(port)

        self.path = "/" + url

    def requests(self, max_redirects = 3) -> object:
        if self.scheme == "about":
            return "",  None
        
        if max_redirects <= 0:
            raise Exception("Too many redirects")

        # create a socket to connect to host
>>>>>>> master
        s = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP,
        )

<<<<<<< HEAD
        if ":" in self.host:
            self.host, port = self.host.split(":", 1)
            self.port = int(port)

        # connect to host change port based on scheme
=======
        # connect to different schemes
>>>>>>> master
        if self.scheme == "http":
            self.port = 80

        elif self.scheme == "https":
            self.port = 443
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname=self.host)

<<<<<<< HEAD
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
=======
        elif self.scheme == "file":
            return open(self.host, "r").read()
        
        elif self.scheme == "data:text/html":
            return checkEntity(self.host), None
        
        s.connect((self.host, self.port))

        self.encoding = "gzip"

        # send data via send method
        request = "GET {} HTTP/1.0\r\n".format(self.path)
        request += "Host: {}\r\n".format(self.host)
        request += "Connection: {}\r\n".format(self.connection)
        request += "Accept-Encoding: {}\r\n".format(self.encoding)
        request += "\r\n"
        s.send(request.encode("utf8"))

        # read the response
        response = s.makefile("rb")
        status_line = response.readline().decode("utf-8")
        status = status_line.split(" ")[1]

        response_headers = {}
        while True:
            line = response.readline().strip()
            if not line:
                break
            key, value = line.decode("utf-8").split(":", 1)
            response_headers[key.lower()] = value.strip()

        # handle gzip encoding
        if "content-encoding" in response_headers and response_headers["content-encoding"] == "gzip":
            response = gzip.GzipFile(fileobj=response)

        # raise error if transfer or content not in headers
        assert "transfer-encoding" not in response_headers

        # allow for redirects
        if status in ["301", "302"] and "location" in response_headers:
            new_url = response_headers["location"]
            self.parse_url(new_url)
            return self.requests(max_redirects - 1)

        # send the data
        content = response.read().decode("utf-8")
        s.close()

        return content, self.tag if hasattr(self, "tag") else None
>>>>>>> master
