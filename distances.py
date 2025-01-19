import openrouteservice
import os
from dotenv import load_dotenv
import openrouteservice.distance_matrix
import json
from tabulate import tabulate

load_dotenv()
""""
This module contains the functions to calclulate the matrix of all the distances between the given cities.

1. get All the Places in two lists and convert them to longitude and latitude

2. Calculate the distance between the two places using the openrouteservice API

3. Visualize the distance matrix in a table format

"""

class distances():
    def __init__(self, placeNames1, placeNames2):
        self.placeNames1 = placeNames1
        self.placeNames2 = placeNames2
        self.placeNameLookup = []
        self.places1 = []
        self.indicesStart = []
        self.indicesEnd = []
        self.data = {}
        self.client = openrouteservice.Client(key=os.environ['ORS_KEY'])

    def convertToCoordinates(self):
        self.places1 = []
        self.indicesStart = []
        self.indicesEnd = []
        for place in self.placeNames1:
            #self.places1.append(self.client.pelias_search(place).get('features')[0].get('geometry').get('coordinates')[::-1])
            self.places1.append(self.client.pelias_search(place).get('features')[0].get('geometry').get('coordinates'))
            # To look up the names later
            self.placeNameLookup.append(place)
            self.indicesStart.append(len(self.places1)-1)
        for place in self.placeNames2:
            #self.places1.append(self.client.pelias_search(place).get('features')[0].get('geometry').get('coordinates')[::-1])
            self.places1.append(self.client.pelias_search(place).get('features')[0].get('geometry').get('coordinates'))
            # To look up the names later
            self.placeNameLookup.append(place)
            self.indicesEnd.append(len(self.places1)-1)
        
        
        #print("-------------------------------------")
        #for place in self.places1:
        #    print(place)
        #print("-------------------------------------")

    def calculateDistances(self):
        # Convert all Places to Coordinates
        self.convertToCoordinates()

        data = (self.client.distance_matrix(self.places1, profile='driving-car', sources=self.indicesStart , destinations=self.indicesEnd, metrics=['distance', 'duration'], units='km'))
        self.data = data
        """"
            Data returns Json with the following structure:

                durations: [
                1st source    [..., ...], => the duration from the nth source to the mth destinations in minutes
                2nd source    [..., ...],
                    ...
                ]
                distances: [
                1st source    [..., ...], => the distance from the nth source to the mth destinations in km
                2nd source    [..., ...],
                    ...
                ]
        """

        with open("data.json", "w", encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def makeTables(self):
        # Extract relevant details
        durations = self.data["durations"]
        distances = self.data["distances"]
        sourceIndeces = self.data["metadata"]["query"]["sources"]
        destinationIndeces = self.data["metadata"]["query"]["destinations"]
        sources = [self.placeNameLookup[int(i)] for i in sourceIndeces]
        destinations = [self.placeNameLookup[int(i)] for i in destinationIndeces]


        # Format source and destination labels
        source_labels = [f"Source {i+1} ({src})" for i, src in enumerate(sources)]
        destination_labels = [f"Destination {i+1} ({dest})" for i, dest in enumerate(destinations)]

        # Create table data for distances
        distance_table = [[""] + destination_labels]  # Header row
        for i, source in enumerate(source_labels):
            row = [source] + [f"{dist:.2f} km" for dist in distances[i]]
            distance_table.append(row)

        # Create table data for durations
        duration_table = [[""] + destination_labels]  # Header row
        for i, source in enumerate(source_labels):
            row = [source] + [f"{(dur / 3600):.2f} hours" for dur in durations[i]]
            duration_table.append(row)

        # Print tables
        """
        print("Distance Matrix:")
        print(tabulate(distance_table, headers="firstrow", tablefmt="grid"))

        print("\nDuration Matrix:")
        print(tabulate(duration_table, headers="firstrow", tablefmt="grid"))
        """
        output_file = "matrix_output.txt"
        with open(output_file, "w") as f:
            f.write("Distance Matrix:\n")
            f.write(tabulate(distance_table, headers="firstrow", tablefmt="grid"))
            f.write("\n\nDuration Matrix:\n")
            f.write(tabulate(duration_table, headers="firstrow", tablefmt="grid"))

    def run(self):
        self.calculateDistances()
        self.makeTables()



if __name__ == "__main__":
    von = ["München", "Aachen", "Darmstadt", "Berlin", "Karlsruhe", "Bonn", "Freiburg", "Dresden", "Frankfurt", "Heidelberg", "Bremen", "Hamburg", "Stuttgart", "Dortmund", "Furtwangen", "Reutlingen", "Tübingen", "Erfurt", "Leipzig"]
    nach = ["Berlin", "Hannover", "Frankfurt", "Gießen", "Leipzig", "München", "Stuttgart"]

    distances = distances(von,nach)
    distances.run()

    