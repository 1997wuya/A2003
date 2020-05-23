"""
web server
为使用者提供一个类，
使用这可以快速的搭建web服务，
展示自己的网页
"""
from socket import *
from select import select
import re


# 主体功能
class HTTPServer:
    def __init__(self, host='0.0.0.0', port=8080, dir=None):
        self.host = host
        self.port = port
        self.dir = dir
        self.rlist = []
        self.wlist = []
        self.xlist = []
        self._sockfd()
        self._bind()

    def _sockfd(self):  # 单下划线 保护变量 双下划綫 私有变量
        self.sockfd = socket()
        self.sockfd.setblocking(False)

    def _bind(self):
        self.addr = (self.host, self.port)
        self.sockfd.bind(self.addr)

    def start(self):
        self.sockfd.listen(5)
        print("Listen the port %d" % self.port)
        self.rlist.append(self.sockfd)
        while True:
            rs, ws, xs = select(self.rlist, self.wlist, self.xlist)
            for r in rs:
                if r is self.sockfd:
                    connfd, addr = r.accept()
                    print("connfd from", addr)
                    connfd.setblocking(False)
                    self.rlist.append(connfd)
                else:
                    self.handle(r)  # 处理客户端连接套接字

    def handle(self, connfd):
        request = connfd.recv(1024 * 10).decode()
        print(request)
        patten = r"[A-Z]+\s+(?P<info>/\S*)"
        try:
            info = re.match(patten, request).group("info")
            print("请求内容", info)
        except:
            self.rlist.remove(connfd)
            connfd.close()
            return
        else:
            self.sent_data(connfd, info)

    def sent_data(self, connfd, info):
        if info == "/":
            html = self.dir + "/index.html"
        else:
            html = self.dir + info
        try:
            f = open(html, "rb")
        except:
            response = "HTTP/1.1 404 Not Found\r\n"
            response += "Content-Type:text/html\r\n"
            response += "\r\n"
            response += "<h1>Sorry...</h1>"
            response = response.encode()

        else:
            data = f.read()
            response = "HTTP/1.1 200 OK\r\n"
            response += "Content-Type:text/html\r\n"
            response += "Content-Length:%d\r\n" % len(data)
            response += "\r\n"
            response = response.encode() + data
        finally:
            connfd.send(response)


if __name__ == '__main__':
    # 需要用户决定 ： 网络地址 和要发送的数据
    host = '0.0.0.0'
    port = 8000
    dir = "./资料"  # 数据位置

    # 实例化对象，调用方法启动服务
    httpd = HTTPServer(host=host, port=port, dir=dir)
    httpd.start()  # 启动服务
