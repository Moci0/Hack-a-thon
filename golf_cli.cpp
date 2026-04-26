#include "golfData.h"
#include <iostream>
#include <sstream>

using namespace std;

int main(int argc, char* argv[]) {
    if (argc < 2) {
        cout << "Usage: golf_cli <distance> [ClubName=Yards ...]" << endl;
        return 1;
    }

    double distance;
    try {
        distance = stod(argv[1]);
    } catch (...) {
        cout << "Invalid distance. Please provide a numeric value." << endl;
        return 1;
    }

    Golf golf;
    for (int i = 2; i < argc; ++i) {
        string arg = argv[i];
        auto pos = arg.find('=');
        if (pos == string::npos) continue;
        string clubName = arg.substr(0, pos);
        string value = arg.substr(pos + 1);
        try {
            double yards = stod(value);
            golf.setClubDistance(clubName, yards);
        } catch (...) {
            // ignore invalid club values
        }
    }

    string recommendation = golf.chooseClub(distance);
    cout << recommendation << endl;
    return 0;
}
