#!/usr/bin/env python
'''
Try out pydap to fetch the current water level from the NOAA Co-ops
server.  This is a really slow way to pull one data point!
'''
import dap.client

if __name__=='__main__':
    dataset=dap.client.open('http://opendap.co-ops.nos.noaa.gov/dods/IOOS/Raw_Water_Level')
    #
    print 'Dataset keys:'
    for item in dataset.keys(): print '  ',item
    seq = dataset['WATERLEVEL_RAW_PX']
    filt_seq=seq.filter('_STATION_ID="1615680"&_BEGIN_DATE="20060101"&_END_DATE="20060101"&_DATUM="MLLW"') 
    print 'filter keys:'
    for item in filt_seq.keys(): print '  ',item
    #
    # Print the results.  To just get field, do this...
    #
    print 'Just the WL_VALUE field:',filt_seq['WL_VALUE'][:][-1]
    #
    # Fetch all the fields.
    print 'One data point:'
    for item in filt_seq.keys():
	print '  ',item,':',filt_seq[item][:][-1] 
    print  'or...'
    data = filt_seq._get_data()
    print 'Found this many waterlevel points:',len(data)
    print data[-1]
