# -*- coding: UTF-8 -*-
# 解压统计局的数据
import os
import shutil
import rarfile as rar
import zipfile as zip

# print(os.listdir())
# quit()

# 因为懒得装WinRAR又找不到能用的unrar.exe
# 所以用自己装的Bandizip凑活一下
# 反正用一次就不用了

toolPath  = 'D:\\Software\\Bandizip\\Bandizip.exe'
# 统计年鉴压缩包存放目录
oriPath   = 'E:\\Workshop\\URP\\OriData\\'
# 解压路径
dstPath   = 'E:\\Workshop\\URP\\improved-LSTM-to-predition-of-ytapple\\data\\prodRaw\\' 
# 暂存解压文件
cachePath = 'E:\\Workshop\\URP\\Cache\\'
# 解压目标
matchName = '农' 

packListZip = [f for f in os.listdir(oriPath) if ('zip' == f[-3:]) or ('rar' == f[-3:])]

# 解压文件
for pack in packListZip:
    os.system('{} x {}'.format(toolPath, oriPath + pack))
