# Importing needed modules 
import feedparser
import gspread
from bs4 import BeautifulSoup
from datetime import datetime


def does_it_work(event, context):
    try:
        #Setting the RSS feed 
        rss_feed = feedparser.parse('https://ransomfeed.it/rss-complete.php')


        # Authenticating with the serive account created
        gc = gspread.service_account(filename='client_secret.json')
        print("Created Gspread service account")
        # Open a sheet from a spreadsheet in one go
        wks = gc.open("Enter name of sheet here").sheet1
        print("Opened Spreadsheet")

        # Filtering the articles with the information we need
        filtered_articles = []
        temp_dict = {}
        to_keep = ['title','published','summary']
        for i in rss_feed.entries:
            for key in to_keep:
                temp_dict[key] = i[key]
            filtered_articles.append(temp_dict)
            temp_dict={}
        print("Filtered articles")

        # Creating a property called hash code and appending it to the entry.
        # Sanitizing the HTML output(removing the tags) from the summary key from the RSS feed.
        for i in filtered_articles:
            soup = BeautifulSoup(i['summary'], 'html.parser')
            i['hash_code'] = (soup.find('i')).get_text()
            soup = BeautifulSoup(i['summary'], 'html.parser')
            i['summary'] = soup.get_text()
        print("Cleaned summary and extracted the hash code")

        # Loading the previous hash values in the sheet
        hash_values = wks.col_values(4)[1:]
        print("Loaded the previous hash values from sheet")

        # Filtering out the articles in the RSS feed that are not in the sheet already
        to_be_added = []
        for article in filtered_articles:
            if article['hash_code'] not in hash_values:
                formatted_date = datetime.strptime(article['published'], '%a, %d %b %Y %H:%M:%S %Z')
                formatted_date = formatted_date.strftime('%Y-%m-%d %H:%M:%S %Z')
                article['published'] = formatted_date
                to_be_added.append(article)
        print("Filtered the articles that are not in the sheet")

        # Entering all the articles into a list, so that we can send the data in one shot.
        row_data = []
        data_to_be_sent = []
        for i in to_be_added:
            for key in i:
                row_data.append(i[key])
            data_to_be_sent.append(row_data)
            row_data = []
        if not len(data_to_be_sent):
            print("Sheet up to date!")
        else:
            print("Data ready to be sent")
             # Uploading the data
            wks.append_rows(data_to_be_sent)
            print("Data uploaded")
        return("Function has ran succesfully")
    except Exception as e:
        print(e)
        return(e)