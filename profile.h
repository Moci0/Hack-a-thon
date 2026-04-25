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
        
       Profile(string firstName, string lastName, string email, string password);// Parameterized constructor to initialize profile information
        void displayAccountInfo(string firstName, string lastName, string email);
        bool login(string email, string password);// Login function to verify email and password
     

        
    private:
        string firstName;
        string lastName;
        string email;
        string password;
       

};
#endif