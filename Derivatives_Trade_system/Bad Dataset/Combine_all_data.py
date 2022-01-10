import os
import glob
import pandas as pd

extension = "csv"
year_list = ["2010","2011","2012","2013","2014","2015","2016",
             "2017","2018","2019"]
month_list = ["January","February","March","April","May","June","July",
             "August","September","October","November","December"]
for year in year_list:
    for month in month_list:
        os.chdir("/Users/feng/Downloads/cs261dummydata/derivativeTrades/"+year+"/"+month)
        all_filenames = [i for i in glob.glob('*.{}'.format(extension))]
        combined_csv = pd.concat([pd.read_csv(f) for f in all_filenames ])
        combined_csv.to_csv( "/Users/feng/Desktop/1/"+year+month+".csv", index=False,
                            encoding='utf-8-sig')

os.chdir("/Users/feng/Desktop/1")
extension = "csv"
all_filenames = [i for i in glob.glob('*.{}'.format(extension))]
combined_csv = pd.concat([pd.read_csv(f) for f in all_filenames ])
combined_csv.to_csv( "/Users/feng/Desktop/hugeData.csv", index=False,
                            encoding='utf-8-sig')
