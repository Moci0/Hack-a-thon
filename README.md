# Hack-a-thon
python3 draw_map.py course_data/course_{number}.json //to view map

DASHBOARD MODE
  python -m pip install {required components}
  python3 app.py
  open http://127.0.0.1:5000/
  python3 caddie_live_v5.py --dashboard
    choose course 2;
    use arrow keys, N to jump to next hole, = to jump further, - to jump less
    


C++ CLUB RECOMMENDER (optional)
  g++ golf_cli.cpp golfData.cpp -o golf_cli
  # or use make
  make

If the compiled C++ helper exists, the dashboard backend will use it for the club recommendation.
The dashboard will receive live updates from the simulator and recommend a club based on the distances you enter.
