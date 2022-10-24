import time
import subprocess


def response_time(ip):
    current_time = time.time()
    proc = subprocess.Popen(['ping', '-c', '1', ip], stdout=subprocess.PIPE)
    proc.communicate()
    ttl = time.time() - current_time
    return ttl*1000


if __name__ == '__main__':
    print(response_time('118.25.94.36'))
