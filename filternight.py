# Filter Night data from the CSV

with open("ndvi-weatherkit-clouds-lands.csv", 'r') as initialCSV:
    initialCSV.readline()
    for i in range(1, 479):
        line = initialCSV.readline()

        landType = line.split(",")[-1].replace("\"", "")[:-1]
        if landType != "Night":
            with open("ndvi-weatherkit-clouds-lands-filteredNight.csv", 'a') as newCSV:
                newCSV.write(line)