#include "golfData.h"
#include <cmath>
#include <iostream>
#include <unordered_map>
using namespace std;

Golf::Golf() {
    // Initialize club distances (example values, can be adjusted based on actual club performance)
    clubDistances["Driver"] = 230.0; // Average distance for a driver
    clubDistances["3-Wood"] = 210.0; // Average distance for a 3-wood
    clubDistances["5-Wood"] = 195.0; // Average distance for a 5-wood
    clubDistances["2-Iron"] = 180.0; // Average distance for a 2-iron
    clubDistances["3-Iron"] = 170.0; // Average distance for a 3-iron
    clubDistances["4-Iron"] = 160.0; // Average distance for a 4-iron
    clubDistances["5-Iron"] = 150.0; // Average distance for a 5-iron
    clubDistances["6-Iron"] = 140.0; // Average distance for a 6-iron
    clubDistances["7-Iron"] = 130.0; // Average distance for a 7-iron
    clubDistances["8-Iron"] = 120.0; // Average distance for an 8-iron
    clubDistances["9-Iron"] = 110.0; // Average distance for a 9-iron
    clubDistances["Pitching Wedge"] = 100.0; // Average distance for a pitching wedge
    clubDistances["Sand Wedge"] = 80.0; // Average distance for a sand wedge 
    //metres

}

double Golf::getDistanceYards(double lat1, double lon1, double lat2, double lon2, double yardage){
    const double r = 6371e3; // Earth radius in meters
    lat1 = lat1 * M_PI / 180.0; // Convert latitude to radians
    lon1 = lon1 * M_PI / 180.0; // Convert longitude to radians
    lat2 = lat2 *M_PI / 180.0; // Convert latitude to radians
    lon2 = lon2 * M_PI / 180.0; // Convert longitude to radians

    double dlat = lat2 - lat1; // Difference in latitude
    double dlon = lon2 - lon1; // Difference in longitude

    double a = sin(dlat / 2) * sin(dlat / 2) + cos(lat1) * cos(lat2) * sin(dlon / 2) * sin(dlon / 2); // Haversine formula because it accounts for the curvature of the Earth
    double c = 2 * atan2(sqrt(a), sqrt(1 - a));// Angular distance in radians
    double distance = r * c; // Distance in meters
    double distanceLeft = yardage - metersToYards(distance); // Convert distance to yards and return the distance left to the hole
    return distanceLeft;

}

double Golf::getDistanceMeter(double lat1, double lon1, double lat2, double lon2, double meterage){
    const double r = 6371e3; // Earth radius in meters
    lat1 = lat1 * M_PI / 180.0; // Convert latitude to radians
    lon1 = lon1 * M_PI / 180.0; // Convert longitude to radians
    lat2 = lat2 *M_PI / 180.0; // Convert latitude to radians
    lon2 = lon2 * M_PI / 180.0; // Convert longitude to radians

    double dlat = lat2 - lat1; // Difference in latitude
    double dlon = lon2 - lon1; // Difference in longitude

    double a = sin(dlat / 2) * sin(dlat / 2) + cos(lat1) * cos(lat2) * sin(dlon / 2) * sin(dlon / 2); // Haversine formula because it accounts for the curvature of the Earth
    double c = 2 * atan2(sqrt(a), sqrt(1 - a));// Angular distance in radians
    double distance = r * c; // Distance in meters
    double distanceLeft = meterage - distance; // Return the distance left to the hole
    return distanceLeft;

}

double Golf::metersToYards(double meters) {
    double yards = meters * 1.09361; // Convert meters to yards
    return yards;
}

double Golf::yardsToMeters(double yards) {
    double meters = yards / 1.09361; // Convert yards to meters
    return meters;
}
string Golf::updateAverageYards(string clubName, double distanceHit){
    if (clubDistances.find(clubName) != clubDistances.end()) {// Check if the club exists in the map
        clubDistances[clubName] = (clubDistances[clubName] + distanceHit) / 2; // Update the average distance for the club
        return "Average distance for " + clubName + " updated to " + to_string(clubDistances[clubName]) + " yards.";
    } else {
        return "Club not found. Please enter a valid club name.";
    }

}
string Golf::updateAverageMeters(string clubName, double distanceHit){
    if (clubDistances.find(clubName) != clubDistances.end()) {// Check if the club exists in the map
        clubDistances[clubName] = (clubDistances[clubName] + yardsToMeters(distanceHit)) / 2; // Update the average distance for the club
        return "Average distance for " + clubName + " updated to " + to_string(clubDistances[clubName]) + " meters.";
    } else {
        return "Club not found. Please enter a valid club name.";
    }

}

void Golf::displayCourseInfo(string courseName, string location, int par, double distance, bool inMeters) {
    cout << "Course Name: " << courseName << endl;
    cout << "Location: " << location << endl;
    cout << "Par: " << par << endl;

    if (inMeters) {
        cout << "Distance: " << yardsToMeters(distance) << " meters" << endl;
    } else {
        cout << "Distance: " << distance << " yards" << endl;
    }
}

Golf::Golf(string courseName, string location, int par, double distance) {
    this->courseName = courseName;
    this->location = location;
    this->par = par;
    this->distance = distance;
}

void Golf::scoreCard(int strokes, int par) {
    int holeNum = 1; // Assuming a default hole number

    for (int i = 0; i < 18; i++) { // Loop through 18 holes
        
        cout << "Hole " << holeNum << ": Par " << par << ", Strokes " << strokes << endl;
        holeNum++;
       
    }

    int score = calculateScore(strokes, par);
    cout << "Total Score: " << score << endl;
}