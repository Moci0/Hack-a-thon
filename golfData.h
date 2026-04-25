#ifndef GOLF_H
#define GOLF_H
#include <iostream>
#include <string>
#include <cmath>
#include <unordered_map>
using namespace std;
class Golf
{
    
    public:
        Golf();// Default constructor
        
        double getdistance(double lat1, double lon1, double lat2, double lon2, double yardage);
       // double getvectordistance(double x1, double y1, double x2, double y2);

        double metersToYards(double meters);// Converts meters to yards
        double yardsToMeters(double yards);// Converts yards to meters
        void displayCourseInfo(string courseName, string location, int par, double distance);// Displays course information
        Golf(string courseName, string location, int par, double distance);// Parameterized constructor to initialize course information

        //choose club based on distance to the hole and person hit distances with each club
        string chooseClub(double distanceToHole);
        int calculateScore(int strokes, int par);// Calculates the score based on strokes and par

    private:
        string courseName;
        string location;
        int par;
        double distance;    
       unordered_map<string, double> clubDistances; // Map to store club names and their distances

};
#endif