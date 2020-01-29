import sys
import socket
from ftplib import FTP
from socket import _GLOBAL_DEFAULT_TIMEOUT

__all__ = ["FTP", "error_reply", "error_temp", "error_perm", "error_proto",
           "all_errors"]

MSG_OOB = 0x1

FTP_PORT = 21
MAXLINE = 8192

class Error(Exception): pass
class error_reply(Error): pass
class error_temp(Error): pass
class error_perm(Error): pass
class error_proto(Error): pass

all_errors = (Error, OSError, EOFError)

CRLF = '\r\n'
B_CRLF = b'\r\n'

class ftpUploadModule(FTP):

    def __init__(self, host='', user='', passwd='', acct='',
                 timeout=_GLOBAL_DEFAULT_TIMEOUT, source_address=None):

        FTP.__init__(self, host, user, passwd, acct, timeout, source_address)
        self.stop = False
        self.pause = False
    
    def storbinary(self, cmd, fp, blocksize=8192, callback=None, rest=None):
        
        self.voidcmd('TYPE I')
        with self.transfercmd(cmd, rest) as conn:
            while 1:
                buf = fp.read(blocksize)

                if self.stop or self.pause:
                    break

                if not buf:
                    break
                
                conn.sendall(buf)

                if callback:
                    callback(buf)

            if _SSLSocket is not None and isinstance(conn, _SSLSocket):
                conn.unwrap()
        return self.voidresp()

try:
    import ssl
except ImportError:
    _SSLSocket = None
else:
    _SSLSocket = ssl.SSLSocket