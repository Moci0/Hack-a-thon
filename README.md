# Hack-a-thon
python3 draw_map.py course_data/course_{number}.json //to view map
python3 caddie_live.py  //for live demo

LIVE VERSION
  python -m install {missing package}
  python3 caddie_live_v5.py //live new demo use arrow keys, N to jump to next hole, = to jump further, - to jump less
    Choose course 2;

DASHBOARD MODE
  pip install -r requirements.txt
  python3 app.py
  open http://127.0.0.1:5000/
  python3 caddie_live_v5.py --dashboard

C++ CLUB RECOMMENDER (optional)
  g++ golf_cli.cpp golfData.cpp -o golf_cli
  # or use make
  make

If the compiled C++ helper exists, the dashboard backend will use it for the club recommendation.
The dashboard will receive live updates from the simulator and recommend a club based on the distances you enter.
