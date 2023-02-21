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

# %%
# 初始化
import os
import numpy as np
import pandas as pd
import ftplib as ftp
from tqdm import tqdm

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

# 连接ftp站点
ftpSite = ftp.FTP()
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

dataPath  = '../data/climData/'         # 数据保存路径
cachePath = '../data/climData/cache/'   # 压缩包和nc文件暂存路径
timeRange = [199201,202312]             # 时间段
latRange  = [36.45, 38.45]              # latitude Range
lonRange  = [119.55, 122.05]            # longitude Range

# %% [markdown]
# 注意：**不建议**在notebook内直接运行下面一段代码，貌似jupyter对进度显示的支持度不太行

# %%
pathName   = 'Data_forcing_03hr_010deg/'
folderList = ['Temp', 'Prec', 'Pres', 'SRad', 'SHum', 'LRad', 'Wind']

withIn     = lambda val, range: True if val >= min(range) and val <= max(range) else False

fileCount  = 0
for folderName in folderList:
    path      = pathName + folderName + '/'
    fileCount += len(ftpSite.nlst(path)[2:])
pbar = tqdm(total=fileCount)

for folderName in folderList:
    path     = pathName + folderName + '/'
    fileList = ftpSite.nlst(path)[2:]
    for file in fileList:
        fileName = file.split('.nc.gz')[0]
        time = int(fileName[-6:])
        if not withIn(time, timeRange):
            pbar.write('{} not in range, skipped.'.format(fileName))
            pbar.update(1)
            continue
        elif isSavedFile(fileName, dataPath):
            pbar.write('{} is already saved.'.format(fileName))
            pbar.update(1)
            continue
        # else:
        #     ftpSite.retrbinary('retr {}'.format(path + file), \
        #         open(cachePath + 'cache.nc.gz', 'wb').write)
        #     pbar.write

# %%
# from time import sleep
# pbarT = tqdm(total=100)
# for i in range(100):
#     pbarT.update(i)
#     sleep(0.5)
# pbarT.close()


