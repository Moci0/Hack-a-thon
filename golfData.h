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
        
        double getDistanceYards(double lat1, double lon1, double lat2, double lon2, double yardage);
        double getDistanceMeter(double lat1, double lon1, double lat2, double lon2, double meterage);

       // double getvectordistance(double x1, double y1, double x2, double y2);

        double metersToYards(double meters);// Converts meters to yards
        double yardsToMeters(double yards);// Converts yards to meters
        void setClubDistance(const string& clubName, double yards);// Override the average distance for a specific club

        //update user average
        string updateAverageYards(string clubName, double distanceHit);// Updates the average distance for a specific club based on user input
        string updateAverageMeters(string clubName, double distanceHit);
        void displayCourseInfo(string courseName, string location, int par, double distance, bool inMeters);// Displays course information
        Golf(string courseName, string location, int par, double distance);// Parameterized constructor to initialize course information
        
        void scoreCard(int strokes, int par);// Displays the scorecard based on strokes and par
        //choose club based on distance to the hole and person hit distances with each club
        string chooseClub(double distanceToHole);
        int calculateScore(int strokes, int par);// Calculates the score based on strokes and par
        
        //weather conditions and how they affect play and strategy advice
        string weatherImpact(string weatherCondition);// Provides advice on how different weather conditions can impact play and suggests strategies to adapt to those conditions
        void displayWeatherAdvice(string weatherCondition);// Displays specific advice for playing in different weather conditions
    private:
        string courseName;
        string location;
        int par;
        double distance;    
        unordered_map<string, double> clubDistances; // Map to store club names and their distances

};
#endif