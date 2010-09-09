#!/usr/bin/env python
import dap.client
import urllib
if __name__=='__main__':
    dataset=dap.client.open('http://opendap.co-ops.nos.noaa.gov/dods/IOOS/Raw_Water_Level')
    seq = dataset['WATERLEVEL_RAW_PX']
    reqStr=urllib.quote('_STATION_ID="1615680"&_BEGIN_DATE="20060101 10:06"&_END_DATE="20060101 10:06"&_DATUM="MLLW"')
    print 'reqStr:',reqStr
    filt_seq=seq.filter(reqStr) 
    data = filt_seq._get_data() # Is this bad - using private method?
    print 'Found this many waterlevel points:',len(data)
    print data #[-1]
