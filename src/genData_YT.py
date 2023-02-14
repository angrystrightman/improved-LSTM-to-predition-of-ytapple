import os,re
import xlrd
import pandas as pd
import numpy  as np

# validData = lambda value: value if type(value) == type(float(1.0)) else 0

def validData(value):
    if type(value) == type(float(1.0)):
        return value
    else:
        try:
            return float(eval(str(value).replace(' ','')))
        except:
            return 0

saveLoc   = '../data/prodData_YT.csv'  # 设置：存储路径
dataPath  = '../data/prodRaw/'        # 设置：数据路径
print(os.listdir(dataPath))
fileList  = [i for i in os.listdir(dataPath) if 'xls' in i]

dataKeys  = ['Name', 'Time', 'Prod', 'Area', 'AverProd']
data      = pd.DataFrame(columns=dataKeys)
dataDict  = dict.fromkeys(dataKeys, np.nan)
count     = 0
pattern   = re.compile('.*(县|区).*果品.*')

areaNameListRaw = []
areaNameList    = []
print('Fetch name...')
# 只选取重复数据，方便使用
for f in fileList:
    try:
        book = xlrd.open_workbook(dataPath+f)
    except:
        print("Error when reading: {}".format(f))
        continue
    tNames  = book.sheet_names()
    tarName = ''
    for name in tNames:
        if pattern.search(name):
            tarName = name
            break
    if tarName != '':
        table = book.sheet_by_name(tarName)
    elif len(book.sheet_names()) == 1:
        table = book.book.sheets()[0]
    else:
        continue
    for name in table.col_values(0)[7:]:
        name = str(name).split(' ')[-1]
        areaNameListRaw.append(name)

for i in areaNameListRaw:
    if areaNameListRaw.count(i) == 20:
        if i not in areaNameList:
            areaNameList.append(i)
print('xxxx', end=' ')
for i in areaNameList:
    print(i, end=' ')
print('')

print('\nGen data...\n')
# 获取数据并写入DataFrame
for f in fileList:
    print(f[-8:-4], end=' ')
    try:
        book = xlrd.open_workbook(dataPath+f)
    except:
        print("Error when reading: {}".format(f))
        continue
    tNames  = book.sheet_names()
    tarName = ''
    for name in tNames:
        if pattern.search(name):
            tarName = name
            break
    if tarName != '':
        table = book.sheet_by_name(tarName)
    else:
        continue
    # 每一行（一个区/县）的数据
    for i in range(7, table.nrows):
        row      = table.row_slice(i)
        areaName = str(row[0].value)[-3:] # .split(' ')[-1]
        if len(areaName) == 0:
            # 空行/数据残缺，跳过
            continue
        # elif areaName in areaNameList:
        else:
            print(areaName, end=' ')
            data.loc[count]             = dataDict
            data.loc[count]['Name']     = areaName
            data.loc[count]['Time']     = int(f[-8:-4]) - 1
            data.loc[count]['Prod']     = validData(row[3].value)
            data.loc[count]['Area']     = validData(row[10].value)
            data.loc[count]['AverProd'] = data.loc[count]['Prod'] / data.loc[count]['Area'] \
                if data.loc[count]['Area'] else 0
            if data.loc[count]['Area'] == 0:
                continue
            else:
                count += 1
    print('')

data.to_csv(saveLoc, index=False)