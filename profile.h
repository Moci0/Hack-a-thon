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
        void displayAccountInfo();// Displays account information
        bool login(string email);// Login function to verify email 
        void updateHandicap(int newHandicap);// Function to update the player's handicap

        int getHandicap();// Function to retrieve the player's current handicap
        string getEmail();// Function to retrieve the player's email
        string getFirstName();// Function to retrieve the player's first name
        string setEmail(string newEmail);// Function to update the player's email
        string setFirstName(string newFirstName);// Function to update the player's
        string setLastName(string newLastName);// Function to update the player's last name
        string getLastName();// Function to retrieve the player's last name
        int sethandicap(int newHandicap);// Function to update the player's handicap

     

        
    private:
        string firstName;
        string lastName;
        string email;
        int handicap; // Golf handicap to track player's skill level
       

};
#endif