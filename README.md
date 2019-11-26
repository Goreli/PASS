# PASS
Synchronous Data Scraper written in Python

Gets data from the [Police Auctions web site](https://www.policeauctions.com) and writes it to a Mongo database in a format suitable for subsequent analysis. 

The environment for this project was created using the following commands:
```
conda create -n pass python=3.7.3
conda activate pass

conda install python-dateutil
conda install -c anaconda beautifulsoup4
conda install -c anaconda pytz
conda install pymongo
conda install requests
conda install -c conda-forge lxml
```
Make sure to start the Mongo DB server before starting this program. Start the program by navigating to the pass directory and executing the following command:

    python pass.py
