#include "profile.h"
#include <iostream>
#include <string>
using namespace std;
Profile::Profile() {
    // Default constructor
    firstName = "";
    lastName = "";
    email = "";
    age = 0;
    handicap = 0.0;
}
Profile::Profile(string firstName, string lastName, string email) {
    // Parameterized constructor to initialize profile information
    this->firstName = firstName;
    this->lastName = lastName;
    this->email = email;
    this->age = 0; // Default age
    this->handicap = 0.0; // Default handicap
}
void Profile::displayAccountInfo() {
    cout << "Account Information:" << endl;
    cout << "Name: " << firstName << " " << lastName << endl;
    cout << "Email: " << email << endl;
    cout << "Handicap: " << handicap<< endl;
}

bool Profile::login(string email){
    if(this->email == email){
        cout << "Login successful!" << endl;
        return true;
    } else {
        cout << "Login failed. Email not found." << endl;
        return false;
    }
}
//getters and setters
int Profile::getHandicap() {
    return handicap;
}
string Profile::getEmail(){
    return email;
}
string Profile::getFirstName() {
    return firstName;
}
string Profile::setEmail(string newEmail) {
    email = newEmail;
    return "Email updated successfully.";
}
string Profile::setFirstName(string newFirstName) {
    firstName = newFirstName;
    return "First name updated successfully.";
}
string Profile::setLastName(string newLastName) {
    lastName = newLastName;
    return "Last name updated successfully.";
}
string Profile::getLastName() {
    return lastName;
}