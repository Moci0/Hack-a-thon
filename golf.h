#ifndef GOLF_H
#define GOLF_H
#include <iostream>
#include <string>
using namespace std;
class Golf
{
    
    public:
        Golf();// Default constructor
        
        double getdistance(double lat1, double lon1, double lat2, double lon2, double yardage);
        double metersToYards(double meters);// Converts meters to yards
        double yardsToMeters(double yards);// Converts yards to meters
        void displayCourseInfo(string courseName, string location, int par, double distance);// Displays course information
    private:
        string courseName;
        string location;
        int par;
        double distance;    
       

};
#endif