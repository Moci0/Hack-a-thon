all: golf_cli

golf_cli: golf_cli.cpp golfData.cpp
	g++ golf_cli.cpp golfData.cpp -o golf_cli

run-backend:
	python3 app.py

clean:
	rm -f golf_cli
