

import os
import json

import keys


class DataRW:
    def __init__(self, datafileName='data.file'):
        
       
        self.datafileName = datafileName

       
        if not os.path.exists(self.datafileName):
            f = open(self.datafileName, 'w')
            f.close()

    def writeData(self, data):
        
        
        f = open(self.datafileName, 'r')
        lines = f.readlines()
        f.close()

        
        if len(lines) > 0:
            if lines[0] == '':
                s = ''
            else:
                s = '\n'
        else:
            s = ''

       
        f = open(self.datafileName, 'a')
        s += json.dumps(data)
        f.write(s)
        f.close()

    def comboExists(self, title, type):
       
        f = open(self.datafileName, 'r')
        lines = f.readlines()
        f.close()

        for line in lines:
            data = json.loads(line)

            if data[keys.OUTLET_TITLE] == title and data[keys.TYPE] == type:
                return True

        return False

    def exists(self, title):
        
        return self.comboExists(title, keys.TYPE_CODE_ON) | self.comboExists(title, keys.TYPE_CODE_OFF)

    def remove(self, title):
       
        f = open(self.datafileName, 'r')
        lines = f.readlines()
        f.close()

        out = []

        for line in lines:
            data = json.loads(line)

            if data[keys.OUTLET_TITLE] != title:
                out.append(line)

        f = open(self.datafileName, 'w')
        f.writelines(out)
        f.close()

    def getTitles(self):
       
        f = open(self.datafileName, 'r')
        lines = f.readlines()
        f.close()

        titles = []

        for line in lines:
            data = json.loads(line)

            if data[keys.OUTLET_TITLE] not in titles:
                titles.append(data[keys.OUTLET_TITLE])

        titles.sort()

        return titles

    def _getParameters(self, title, type):
        
        f = open(self.datafileName, 'r')
        lines = f.readlines()
        f.close()

        for line in lines:
            data = json.loads(line)

            if data[keys.OUTLET_TITLE] == title and data[keys.TYPE] == type:
                output = (data[keys.CODE], data[keys.ONE_HIGH_TIME],
                          data[keys.ONE_LOW_TIME], data[keys.ZERO_HIGH_TIME],
                          data[keys.ZERO_LOW_TIME], data[keys.INTERVAL])
                break

        return output

    def getOnParameters(self, title):
        
        return self._getParameters(title, keys.TYPE_CODE_ON)

    def getOffParameters(self, title):
       
        return self._getParameters(title, keys.TYPE_CODE_OFF)
