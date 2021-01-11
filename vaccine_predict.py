import csv
import matplotlib.pyplot as plt
import numpy as np
import urllib3
import datetime

now = datetime.datetime.now()

# Get the latest data
http = urllib3.PoolManager()
contents = http.request('GET', 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations.csv')
# use the world data file because the USA data file has extra commas
# separating vaccine types in the URL below
#contents = http.request('GET', 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/country_data/United States.csv')


# set up the population numbers
alladults = 249000000
adultherd = int(.75 * alladults)
everyone = 331000000

# substitue interval number for actual date
# and just count intervals for graphing one per day
# parse and store the current data points for plotting
i =1
currentrow = 1
firstentry = 1
interval = [0]
vaccines = [0]

for row in contents.data.decode('utf-8').splitlines():
    if row.split(",")[0] == "United States":
        if row.split(",")[3] != "":
            last =  row.split(",")[3]
        if row.split(",")[3] != "":
            val = int(row.split(",")[3])
            interval.append(i)
            vaccines.append(val)
        else:
            val = int(last)
            interval.append(i)
            vaccines.append(val)
        if firstentry == 1:
            firstdate = row.split(",")[2]
            firstentry = 0
        i = i + 1

# Process a csv file method. Abandoned due to smallish data set 
# and avoiding file IO - DP 01/07/2021
#with open('/tmp/vaccinations.csv', newline='') as csvfile:
#    reader = csv.reader(csvfile, delimiter=',', quotechar='|')
#    i = 1
#    for row in reader:
#        if row[0] == "United States":
#            if row[3] != "":
#                last =  row[3]
#            if row[3] != "":
#                #print (i, row [3])
#                interval.append(i)
#                vaccines.append(row [3])
#            else:
#                #print (i, last)
#                interval.append(i)
#                vaccines.append(last)
#            i = i + 1


# do a 3rd order polynomial fit to the current data with NumPy
fit = np.polyfit(interval, vaccines, 3)
fitline = np.poly1d(fit)

x1 = 1
ahflag = 1
aaflag = 1
ipredict=[0]
ivaccine=[0]

# set the limit on the while loop 
# to determine timeframe for all, all adults, or adult herd 
# extrapolate the data for the various thresholds by 
# incrementing the number of days
while fitline(x1) < everyone:
    ipredict.append(x1)    
    ivaccine.append(fitline(x1))
    if fitline(x1) > adultherd and ahflag == 1:
        adultherddays = x1
        ahflag = 0
    if fitline(x1) > alladults and aaflag == 1:
        alladultdays = x1
        aaflag = 0
    x1 = x1 + 1

# figure the dates for each threshold
startdate = datetime.datetime.strptime(firstdate, "%Y-%m-%d")
adultherddate = startdate + datetime.timedelta(days=adultherddays)
alladultdate = startdate + datetime.timedelta(days=alladultdays)
finaldate = startdate + datetime.timedelta(days=x1)
nowdate = startdate + datetime.timedelta(days=i - 1)

#Plot the data
plt.style.use('bmh')
plt.figure(figsize=(13.1, 8.6))
plt.ticklabel_format(axis="y", style="plain")
plt.hlines(adultherd, 0, x1, "y")
plt.hlines(alladults, 0, x1, "g")
plt.hlines(everyone, 0, x1, "g")
plt.hlines(val, 0, x1, "k")
plt.plot(ipredict, ivaccine, "m+")
plt.plot(interval, vaccines, "b")
plt.legend(['Extrapolated Progress based on Actual', 'Current Actual Progress'])
plt.title('US Vaccination Progress to Total US Population with Adult Immunity Levels - Based on Adults Vaccinated\nUpdated as of ' + str(now))
plt.ylabel('Total US Vaccinations')
plt.xlabel('Total Days Since US Start')
plt.xlim([0,x1])
plt.text(-3, -35000000, startdate.date())
plt.text(x1 - 3, -35000000, finaldate.date())
plt.text(40, adultherd+5000000, "75% Adult Herd Immunity - 186750000 Vaccinations")
plt.text(adultherddays, adultherd-9000000, adultherddate.date())
plt.text(40, alladults+5000000, "All Adult Vaccinations - 249000000 Vaccinations")
plt.text(alladultdays, alladults-9000000, alladultdate.date())
plt.text(40, everyone+5000000, "Total US Population - 331000000 Vaccinations")
plt.text(i - 5, val-10000000, nowdate.date(), color="b")
plt.text(i - 5, val+14000000, "We Are Here", color="b")
plt.text(i - 7, val+5000000, val, color="b")
plt.text(i, val+5000000, "Vaccinations", color="b")
plt.savefig('/tmp/vac_progress.png')

# uncomment below to output the result to a display as well as a file
#plt.show()
