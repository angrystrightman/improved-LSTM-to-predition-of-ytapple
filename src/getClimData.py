# %% [markdown]
# ### 获取气候数据
# 
# 因为直接全部下载会导致数据量过大，所以每下载一个就进行处理，只保留烟台区域的数据
# 
# #### 需求第三方库：
# 
# `numpy`, `pandas`, `tqdm`
# 
# #### 代码
# 
# 此文件主要用于调试，运行时使用`getClimData.py`文件，该文件会阶段性与此文件同步

# %%
import os, gzip
import netCDF4
import numpy as np
import pandas as pd
import ftplib as ftp
from math import ceil
from tqdm import tqdm as tqdmCMD
from tqdm.gui import tqdm as tqdmGUI

# %%
# 定义函数、重载类

def isSavedFile(fileName: str, path:str):
    """
    检测文件是否已经存在  
    ### 参数  
    `fileName`: `str` 文件名  
    `path`: `str` 路径名  
    ### 返回值  
    `bool` 存在则返回True
    """
    if '.nc' in fileName:
        fileName = fileName.split('.nc')[0]
    fileList = [i.split('.csv') for i in os.listdir(path) if '.csv' in i]
    return fileName in fileList

def unpack_gz(src, dst):
    g_file = gzip.GzipFile(src)
    c_file = open(dst, "wb+")
    c_file.write(g_file.read())
    c_file.close()
    g_file.close()

# ftplib中为了增加对TLS支持所以加了一个sslSocket的判断，理论上在这里运行一遍应该能解决下面未定义的错误
try:
    import ssl
except ImportError:
    _SSLSocket = None
else:
    _SSLSocket = ssl.SSLSocket

class myFTP(ftp.FTP):

    def retrbinary(self, cmd, callback, blocksize=8192, rest=None):
        """Retrieve data in binary mode.  A new port is created for you.

        ### Args:
          `cmd`: A RETR command.
          `callback`: A single parameter callable to be called on each
                    block of data read.
          `blocksize`: The maximum number of bytes to read from the
                     socket at one time.  [default: `8192`]
          `rest`: Passed to transfercmd().  [default: `None`]

        ### Returns:
          The response code.
        """
        self.voidcmd('TYPE I')
        fileSize = self.size(cmd.replace('retr ', '')) # 1024进制，单位b
        progBar  = tqdmCMD(total=fileSize)
        with self.transfercmd(cmd, rest) as conn:
            while 1:
                data = conn.recv(blocksize)
                if not data:
                    progBar.close()
                    break
                callback(data)
                progBar.update(blocksize)
            # shutdown ssl layer
            if _SSLSocket is not None and isinstance(conn, _SSLSocket):
                conn.unwrap()
        return self.voidresp()

# %%
# 连接ftp站点
ftpSite = myFTP()
ftpSite.connect(host="ftp2.tpdc.ac.cn", port=6201)
ftpSite.login(user="download_38710462", passwd="59317538")

print(ftpSite.getwelcome())
# print(ftpSite.dir())
# print(ftpSite.nlst('Data_forcing_03hr_010deg/SRad')[2:])

# %%
# 下载测试

# ftpSite.retrbinary('retr Data_forcing_03hr_010deg/SRad/srad_CMFD_V0106_B-01_03hr_010deg_197910.nc.gz',open('t1.nc.gz','wb').write,8192)
# ftpSite.retrbinary('retr Data_forcing_03hr_010deg/SRad/srad_CMFD_V0106_B-01_03hr_010deg_197910.nc.gz',open('t2.nc.gz','wb').write,8192)

# %%
# 参数设置

dataPath   = '../data/climData/'         # 数据保存路径
cachePath  = '../data/climData/cache/'   # 压缩包和nc文件暂存路径
timeRange  = [199201,202312]             # 时间段

# 注意经纬度以0.1度为单位，每个结尾有个0.05的偏移
latRange   = [36.45, 38.45]              # latitude Range 
lonRange   = [119.55, 122.05]            # longitude Range

infoPrint  = False                       # 是否在命令行内输出信息
pathName   = 'Data_forcing_03hr_010deg/' # FTP站点的目标文件夹
folderList = ['Temp', 'Prec', 'Pres', 'SRad', 'SHum', 'LRad', 'Wind']

# %%
withIn     = lambda val, range: True if val >= min(range) and val <= max(range) else False
fileCount  = 0
for folderName in folderList:
    path      = pathName + folderName + '/'
    fileCount += len(ftpSite.nlst(path)[2:])

# %% [markdown]
# 注意：**不建议**在notebook内直接运行下面一段代码，貌似jupyter对GUI进度显示的支持度不太行  
# 因为还有别的进度条也不好做俩命令行的进度条

# %%
pbar      = tqdmGUI(total=fileCount)
def pbarPrint(info: str, isPrint = False):
    pbar.set_description(info)
    if isPrint:
        pbar.write(info)

for folderName in folderList:
    path     = pathName + folderName + '/'
    fileList = ftpSite.nlst(path)[2:]
    for file in fileList:
        fileName = file.split('.nc.gz')[0]
        time = int(fileName[-6:])
        if not withIn(time, timeRange):
            pbarPrint('{}\nnot in range, skipped\n'.format(fileName), infoPrint)
            pbar.update(1)
            continue
        elif isSavedFile(fileName, dataPath):
            pbarPrint('{}\nalready saved\n'.format(fileName), infoPrint)
            pbar.update(1)
            continue
        pbarPrint('{}\ndownloading\n'.format(fileName), infoPrint)
        ftpSite.retrbinary('retr {}'.format(path + file), \
            open(cachePath + 'cache.nc.gz', 'wb').write)
        pbarPrint('{}\nprocessing\n'.format(fileName), infoPrint)
        unpack_gz(cachePath + 'cache.nc.gz', cachePath + 'cache.nc')
        data = netCDF4.Dataset(cachePath + 'cache.nc')
        print(data.variables.keys())
        data.close()
        # os.remove(cachePath + 'cache.nc.gz')
        # os.remove(cachePath + 'cache.nc')
        pbar.update(1)



# %%
# 退出FTP站点
ftpSite.quit()


