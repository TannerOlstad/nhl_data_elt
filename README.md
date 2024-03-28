# NHL API Data Extraction

Welcome to my NHL data extraction project! I wanted to challenge myself with a new data project, which would help me build skills in handling data. I wanted to focus on a Extract, Transform and Load process for data that was in an unfamiliar form to me. This happened to be perfect as I just spent the past few weeks with the NHL API. This notebook will pull data from the the NHL API, which will then be formatted to my preference, and loading to a database, where I will be creating a visualization with this data.

I would also like to thank anyone who has taken the time to look over this project. If you have any feedback or questions, feel free to message me.

-----------------------------------
# ETL

One of the valuable lessons I learned while iterating through the api, was the need to handle errors. Between seasons of the NHL, the format of their data changes. Previously I was examining 2022-2023 data, and wrote code to extract data from those files, while the 2023-2024 data was a different format. To see where my existing code was going wrong, i used print error messages that highlighted where the issues occured. This made troubleshooting easy to fix!

I have also included the output datasets (Which were uploading to a MySql server) as csvs if one is inclined to look at the data.

The code in which I preformed the data ETL, can be found in NHL_etl.py

-----------------------------------
# Analysis
#### Some Light Analysis on our new stored data

My goal was to succesfully extract my data, from my database. This was done with SQLalchemy libary, which worked perfectly.

The first analysis was looking at the games with the most penalty minutes from the NHL 2022-20223 season, specifically the top 10. This visualization highlights the top 10 games. The highest amount of PIM in a game, was 180 (Longer than NHL regulation).

![alt text](https://github.com/TannerOlstad/nhl_data_elt/blob/main/viz/output2.png)

The next analysis was to look at team performance at home, vs the road. 

This could be simply done by making a dataframe with team home wins, road wins, and total games. A for loop was created to add the pValue between the variables, where if the pValue was <0.05 it would be deemed that there was a significant difference in performance for that team.

See:

Null Hypothesis (H0): The win rate for teams in home games is equal to the win rate in road games. Any observed difference is due to random chance.

Alternative Hypothesis (H1): The win rate for teams in home games is not equal to the win rate in road games. There is a statistically significant difference in win rates.

The result revealed two teams were not performing the same at home, as they do on the road. Those two teams are the Chicago Blackhawks and the Colorado Avalanche. It is interesting that there are only two teams who significantly perform differently at home vs the road, and those two teams have vastly different ranks in the NHL's standings. In the future I might investigate how both good and bad teams, can share a trait where they are inconsistent at home vs the road.

See the chart below, highlight those two teams.

![alt text](https://github.com/TannerOlstad/nhl_data_elt/blob/main/viz/output.png)


-----------------------------------

## Conclusion

This project has been interesting to work on, I was able to understand the process of how to gather data from a source such as an API, and process it for use. I learned the fundamentals of working with API endpoints, JSON files and connecting to a Database (A lot easier than I thought). If I was to improve this project, I would like to build out an advanced schema for the database. I would also like to create simple and efficient ways to continue uploading new data to the database.

As a loose schema, here are the tables, and the respective 'teamID' shared across them.

Table      | Keys
-----------| -------------
Standings  | teamAbbrev
Boxscores  | TeamId, teamAbbrev
Players    | TeamId
Goalies    | TeamId


This data extraction process is not flashy, but it will compliment my next project where I work with the data in a visualization software.

The tables of the 4 dataframes will be shown below, just for any curious to what the data looks like.

Thank you for checking out my project!
