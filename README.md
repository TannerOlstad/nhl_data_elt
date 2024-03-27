# NHL API Data Extraction

Welcome to my NHL data extraction project! I wanted to challenge myself with a new data project, which would help me build skills in handling data. I wanted to focus on a Extract, Transform and Load process for data that was in an unfamiliar form to me. This happened to be perfect as I just spent the past few weeks with the NHL API. This notebook will pull data from the the NHL API, which will then be formatted to my preference, and loading to a database, where I will be creating a visualization with this data.

I would also like to thank anyone who has taken the time to look over this project. If you have any feedback or questions, feel free to message me.

-----------------------------------

One of the valuable lessons I learned while iterating through the api, was the need to handle errors. Between seasons of the NHL, the format of their data changes. Previously I was examining 2022-2023 data, and wrote code to extract data from those files, while the 2023-2024 data was a different format. To see where my existing code was going wrong, i used print error messages that highlighted where the issues occured. This made troubleshooting easy to fix!

I have also included the output datasets (Which were uploading to a MySql server) as csvs if one is inclined to look at the data.

The code in which I preformed the data ETL, can be found in NHL_etl.py

-----------------------------------

## Conclusion

This project has been interesting to work on, I was able to understand the process of how to gather data from a source such as an API, and process it for use. I learned the fundamentals of working with API endpoints, JSON files and connecting to a Database (A lot easier than I thought). If I was to improve this project, I would like to build out an advanced schema for the database. I would also like to create simple and efficient ways to continue uploading new data to the database.

As a loose schema, here are the talbes, and the respective 'teamID' shared across them.

Table      | Keys
-----------| -------------
Standings  | TeamId
Boxscores  | TeamId
Players    | TeamId
Goalies    | TeamId


This data extraction process is not flashy, but it will compliment my next project where I work with the data in a visualization software.

The tables of the 4 dataframes will be shown below, just for any curious to what the data looks like.

Thank you for checking out my project!
