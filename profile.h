#ifndef PROFILE_H
#define PROFILE_H
#include <iostream>
#include <string>
using namespace std;
class Profile
{
    
    public:
       
        // Default constructor
        Profile();
        
       Profile(string firstName, string lastName, string email);// Parameterized constructor to initialize profile information
        void displayAccountInfo(string firstName, string lastName, string email, int handicap);// Displays account information
        bool login(string email);// Login function to verify email and password
        void updateHandicap(int newHandicap);// Function to update the player's handicap

     

        
    private:
        string firstName;
        string lastName;
        string email;
        int handicap; // Golf handicap to track player's skill level
       

};
#endif