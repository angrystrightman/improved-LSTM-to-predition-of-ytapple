# 将这个文件放在和py文件同一目录下，然后直接import climDataRead as cdr
# 就可以调用对应的函数了，例如cdr.getFileType
# %%
# 引入必要库函数
import os, re
import numpy as np
import netCDF4 as nc4

# %%
def getFileType(fileName: str):
    ''' 对文件名进行解析，并返回文件的类型
    
        调用格式：fileType, accuracy, period = getFileType(str)

        ### param  
        `filename`: `str` 文件名  
        ### return  
        `tuple` `str`: 以元组形式返回：
        - 数据类型(e.g. lrad)
        - 时间精度(e.g. 01yr)
        - 开始日期&结束日期（另一个元组）

        注意：
        1. 若文件名不匹配，则会返回4个`False`
        2. 所有返回值均为字符串
        3. 开始和结束日期根据时间精度的不同，不一定多长
    ''' 
    # lrad_CMFD_V0106_B-01_01yr_010deg_1979-2018
    # print(fileName)
    p = re.compile(r"([a-z]|[A-Z]{4})_CMFD_V\d{4}_B-01_(.*?)_010deg_(\d*)-(\d*)")
    res = p.search(fileName)    
    if res:
        # print(res.groups())
        rg = res.groups()
        return (rg[0], rg[1], (rg[2], rg[3]))
    else:
        return (False, False, False)

# %%
def formatLocData(loc: float):
    ''' 让经纬度数据对齐网格
        ### param
        `loc`: `float` 经纬度数据
        ### return
        返回离该经纬度最近的一个在nc文件里的数据
    '''
    base = round(round(loc, 2)*100/5)
    if not base%2:
        # 对齐网格
        left  = abs((base-1)/20)
        right = abs((base+1)/20)
        side  = -1 if left < right else 1
        base += side
    return base/20

# %%
def getIndexSingle(ncData, colName, indexVal: float):
    for i in range(len(ncData.variables[colName])):
        if round(ncData.variables[colName][i] - formatLocData(indexVal), 4) == 0:
            return int(i)
    return -1
def getIndexArr(ncData, colName: list, indexVal: np.ndarray):
    retArr = np.zeros(indexVal.shape)
    for i in range(len(colName)):
        for j in range(indexVal.shape[1]):
            retArr[i, j] = getIndexSingle(ncData, colName[i], indexVal[i, j])
    return retArr
def getIndex(ncData, colName, indexVal):
    ''' 寻找某一列数据中特定数据的索引  
        注意：数据必须只有一列（即shape = (n, 1)）

        ### prarm
        `ncData`    : `nc4.Dataset` 通过netCDF4读取的nc数据文件
        `colName`   : `str`|`list`  数据列的名称
        `indexVal`  : `any`|`array` 数据值
        ### return
        `int`: 该数据的索引（若有多个，则返回第一个）
    '''
    if type(indexVal) == np.ndarray:
        if type(colName) != list:
            colName = [colName]
        return getIndexArr(ncData, colName, indexVal)
    else:
        return getIndexSingle(ncData, colName, indexVal)

# %%
def getSquareArea(data, colName, lonRange, latRange):
    ''' 取出一段经纬度范围内的数据

        ### prarm
        `data`      : `nc4.Dataset` 通过netCDF4读取的nc数据文件
        `colName`   : `str`  数据列的名称
        `lonRange`  : `list[1,2]` lontitude的范围 - [start, end]
        `latRange`  : `list[1,2]` latitude的范围 - [start, end]
        ### return
        `MaskedArray`: 3维的数组
        ### example
        `getSquareArea(data, 'temp', [121.35, 121.55], [37.25, 37.55])`
    '''
    index = getIndexArr(data, ['lon', 'lat'], np.array([lonRange, latRange]))
    arr = data.variables[colName][:, int(index[1, 0]):int(index[1, 1]), int(index[0, 0]):int(index[0, 1])]
    return arr
