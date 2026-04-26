#include "profile.h"
#include "golfData.h"
#include <iostream>
#include <string>
#include <limits>

using namespace std;

// Front-end interface placeholder functions
// These will be connected to the front-end in a separate file
namespace FrontEnd {
    void displayWelcome() {
        cout << "======================================" << endl;
        cout << "   Welcome to Golf Tracker Pro!" << endl;
        cout << "======================================" << endl;
        cout << endl;
    }

    void displayMainMenu() {
        cout << "Main Menu:" << endl;
        cout << "1. Create/Update Profile" << endl;
        cout << "2. View Profile" << endl;
        cout << "3. Golf Tools" << endl;
        cout << "4. Exit" << endl;
        cout << "Enter your choice: ";
    }

    void displayProfileMenu() {
        cout << "Profile Menu:" << endl;
        cout << "1. Create New Profile" << endl;
        cout << "2. Update First Name" << endl;
        cout << "3. Update Last Name" << endl;
        cout << "4. Update Email" << endl;
        cout << "5. Update Handicap" << endl;
        cout << "6. Back to Main Menu" << endl;
        cout << "Enter your choice: ";
    }

    void displayGolfToolsMenu() {
        cout << "Golf Tools Menu:" << endl;
        cout << "1. Calculate Distance to Hole" << endl;
        cout << "2. Club Recommendation" << endl;
        cout << "3. Weather Advice" << endl;
        cout << "4. Score Calculator" << endl;
        cout << "5. Update Club Distances" << endl;
        cout << "6. Back to Main Menu" << endl;
        cout << "Enter your choice: ";
    }
}

int main() {
    Profile userProfile;
    Golf golfData;
    int choice;
    bool isLoggedIn = false;
    string tempInput;

    FrontEnd::displayWelcome();

    while (true) {
        if (!isLoggedIn) {
            cout << "\n--- User Login/Registration ---" << endl;
            cout << "1. Login with existing email" << endl;
            cout << "2. Create new profile" << endl;
            cout << "3. Continue as guest" << endl;
            cout << "4. Exit" << endl;
            cout << "Enter your choice: ";
            
            if (!(cin >> choice)) {
                cout << "Invalid input. Please enter a number." << endl;
                cin.clear();
                cin.ignore(numeric_limits<streamsize>::max(), '\n');
                continue;
            }

            switch (choice) {
                case 1: {
                    // Login with existing email
                    cout << "Enter your email: ";
                    cin >> tempInput;
                    isLoggedIn = userProfile.login(tempInput);
                    break;
                }
                case 2: {
                    // Create new profile
                    string firstName, lastName, email;
                    cout << "Enter your first name: ";
                    cin >> firstName;
                    cout << "Enter your last name: ";
                    cin >> lastName;
                    cout << "Enter your email: ";
                    cin >> email;
                    
                    userProfile = Profile(firstName, lastName, email);
                    cout << "Profile created successfully!" << endl;
                    isLoggedIn = true;
                    break;
                }
                case 3: {
                    // Continue as guest
                    cout << "Continuing as guest..." << endl;
                    isLoggedIn = true;
                    break;
                }
                case 4: {
                    cout << "Thank you for using Golf Tracker Pro!" << endl;
                    return 0;
                }
                default:
                    cout << "Invalid choice. Please try again." << endl;
            }
        }

        if (isLoggedIn) {
            FrontEnd::displayMainMenu();
            
            if (!(cin >> choice)) {
                cout << "Invalid input. Please enter a number." << endl;
                cin.clear();
                cin.ignore(numeric_limits<streamsize>::max(), '\n');
                continue;
            }

            switch (choice) {
                case 1: {
                    // Profile management
                    while (true) {
                        FrontEnd::displayProfileMenu();
                        if (!(cin >> choice)) {
                            cout << "Invalid input. Please enter a number." << endl;
                            cin.clear();
                            cin.ignore(numeric_limits<streamsize>::max(), '\n');
                            continue;
                        }

                        switch (choice) {
                            case 1: {
                                string firstName, lastName, email;
                                cout << "Enter your first name: ";
                                cin >> firstName;
                                cout << "Enter your last name: ";
                                cin >> lastName;
                                cout << "Enter your email: ";
                                cin >> email;
                                userProfile = Profile(firstName, lastName, email);
                                cout << "Profile created successfully!" << endl;
                                break;
                            }
                            case 2: {
                                cout << "Enter new first name: ";
                                cin >> tempInput;
                                cout << userProfile.setFirstName(tempInput) << endl;
                                break;
                            }
                            case 3: {
                                cout << "Enter new last name: ";
                                cin >> tempInput;
                                cout << userProfile.setLastName(tempInput) << endl;
                                break;
                            }
                            case 4: {
                                cout << "Enter new email: ";
                                cin >> tempInput;
                                cout << userProfile.setEmail(tempInput) << endl;
                                break;
                            }
                            case 5: {
                                int newHandicap;
                                cout << "Enter new handicap: ";
                                cin >> newHandicap;
                                userProfile.sethandicap(newHandicap);
                                cout << "Handicap updated successfully!" << endl;
                                break;
                            }
                            case 6: {
                                cout << "Returning to main menu..." << endl;
                                break;
                            }
                            default:
                                cout << "Invalid choice. Please try again." << endl;
                        }

                        if (choice == 6) break;
                    }
                    break;
                }
                case 2: {
                    // View profile
                    userProfile.displayAccountInfo();
                    break;
                }
                case 3: {
                    // Golf tools
                    while (true) {
                        FrontEnd::displayGolfToolsMenu();
                        if (!(cin >> choice)) {
                            cout << "Invalid input. Please enter a number." << endl;
                            cin.clear();
                            cin.ignore(numeric_limits<streamsize>::max(), '\n');
                            continue;
                        }

                        switch (choice) {
                            case 1: {
                                // Calculate distance to hole
                                double lat1, lon1, lat2, lon2, yardage;
                                cout << "Enter your current latitude: ";
                                cin >> lat1;
                                cout << "Enter your current longitude: ";
                                cin >> lon1;
                                cout << "Enter hole latitude: ";
                                cin >> lat2;
                                cout << "Enter hole longitude: ";
                                cin >> lon2;
                                cout << "Enter total yardage of hole: ";
                                cin >> yardage;
                                
                                double distanceLeft = golfData.getDistanceYards(lat1, lon1, lat2, lon2, yardage);
                                cout << "Distance left to hole: " << distanceLeft << " yards" << endl;
                                break;
                            }
                            case 2: {
                                // Club recommendation
                                double distanceToHole;
                                cout << "Enter distance to hole (yards): ";
                                cin >> distanceToHole;
                                cout << "Recommended club: " << golfData.chooseClub(distanceToHole) << endl;
                                break;
                            }
                            case 3: {
                                // Weather advice
                                string weather;
                                cout << "Enter weather condition (Rain/Windy/Sunny/Cold): ";
                                cin >> weather;
                                cout << golfData.weatherImpact(weather) << endl;
                                break;
                            }
                            case 4: {
                                // Score calculator
                                int strokes, par;
                                cout << "Enter number of strokes: ";
                                cin >> strokes;
                                cout << "Enter par for the hole: ";
                                cin >> par;
                                int score = golfData.calculateScore(strokes, par);
                                if (score < 0) {
                                    cout << "Score: " << score << " (Under par)" << endl;
                                } else if (score == 0) {
                                    cout << "Score: Even par" << endl;
                                } else {
                                    cout << "Score: +" << score << " (Over par)" << endl;
                                }
                                break;
                            }
                            case 5: {
                                // Update club distances
                                string clubName;
                                double distanceHit;
                                cout << "Enter club name: ";
                                cin >> clubName;
                                cout << "Enter distance hit (yards): ";
                                cin >> distanceHit;
                                cout << golfData.updateAverageYards(clubName, distanceHit) << endl;
                                break;
                            }
                            case 6: {
                                cout << "Returning to main menu..." << endl;
                                break;
                            }
                            default:
                                cout << "Invalid choice. Please try again." << endl;
                        }

                        if (choice == 6) break;
                    }
                    break;
                }
                case 4: {
                    cout << "Thank you for using Golf Tracker Pro!" << endl;
                    return 0;
                }
                default:
                    cout << "Invalid choice. Please try again." << endl;
            }
        }
    }

    return 0;
}