import time
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import requests
import numpy as np
import datetime

from headers import*

number_of_pages = 100
data_frame = []
sites = []
bad_sites = []
processed_sites = load_processed_sites()
processed_posts = load_processed_posts()
bad_sites = load_bad_sites()
print("processed posts",len(processed_posts),len(processed_sites))
#print("processed sites",processed_sites)
#time.sleep(5)
for page in range(number_of_pages):
    print("At page:",page)
    if page+1 == 1:
        website = "https://www.nairaland.com/?"
        #website = "https://www.nairaland.com/links/"+str(100)
    else:
        website = "https://www.nairaland.com/links/"+str(page)
    req = requests.get(website)
    soup = BeautifulSoup(req.text, 'html.parser')
    link_position=0
    post_infor = []
    dfs = []
    for a in soup.find_all('a', href=True):
        #print("Found the URL:",link_position, a['href'])
        if a['href'] in processed_sites or bad_sites:
            #print(a['href'],"Aleady exists")
            #time.sleep(10)
            pass
        else:
            #print(a['href'][:11],a['href'].split())
            link_piece = a['href'][:11]
            site = a['href']
            advert_link = "https://www.nairaland.com/1049481/how-place-targeted-ads-nairaland"
        if link_position>=1 and link_piece == "https://www" and site != advert_link: #118: #range of link that refers to posts
            #if link_position>=58 and link_position<=63: #118: #range of link that refers to posts
            print("Currently at the URL:",page+1, site)
            number_of_pages = get_number_of_pages(a['href'])
            df1 = []
            post_available = True # assume the post has not been removed
            post_proccessed = True # assume that the post was successfully processed
            time.sleep(10)
            for i in range(number_of_pages):
                print("At page",i)
                if i == 0:
                    url = site
                    Author = "Yes"
                else:
                    url = site+"/"+str(i)
                    Author = "No"
                req = requests.get(url)
                soup = BeautifulSoup(req.text, 'html.parser')
                #gets this values from the first page since the section has page numbers
                #in subsequent pages
                text = soup.text
                title = soup.title.text
                #print(title)
                if title == "This topic has been removed or hidden":
                    print("Page has been removed")
                    #total_comments_by_text_slicing = number_of_comments_by_tags_extraction = 0
                    post_available = False
                    break
                else:
                    pass
                number_of_comments_by_tags_extraction = len(get_comments(soup))
                Topic = '-'.join(title.split("-")[:-2])
                Section = title.split("-")[-2]
                Country = title.split("-")[-1]
                Usernames,Gender,Shares,Likes,total_comments_by_text_slicing = \
                get_username_gender_shares_and_likes(text,Topic,number_of_comments_by_tags_extraction)
                    #print("AUTHOR",Author)
                Comments = get_comments(soup)
                Date = get_date(soup)
                #total_comments_by_text_slicing = get_total_comment_by_text_splicing(a,topic)
                if number_of_comments_by_tags_extraction == total_comments_by_text_slicing: #gets good data
                    print(number_of_comments_by_tags_extraction,total_comments_by_text_slicing,len(Date))            
                    post_features = get_post_features(Usernames,Gender,Date,Topic,Author,Section,Country,Comments,Likes,Shares)
                    headers = ["Username","Gender","Date","Topic","Author","Section","Country","Comments","Likes","Shares",]
                    df3 = pd.DataFrame(post_features, columns=headers)
                    df1.append(df3)
                    #print(df3)
                else: #discard wrong data
                    bad_sites.append(site)
                    print("Bad Site!!!")
                    post_proccessed = False
                    print(number_of_comments_by_tags_extraction,total_comments_by_text_slicing)            
                    break
            #if number_of_comments_by_tags_extraction == total_comments_by_text_slicing and total_comments_by_text_slicing > 0: #    process correct data.
            if post_available == True and post_proccessed == True:
                df2 = pd.concat((df for df in df1),axis=0)
                processed_posts.append(df2)
                #print(processed_posts)
                processed_sites.append(site)
                # save it
                save_processed_posts(processed_posts,processed_sites)
            else: # the post is not available or the post was not successfully processed
                bad_sites.append(site)
                save_bad_sites(bad_sites)
                print("Discarding the link as it either unavailable or was not successfully processed")
        else:
            pass
                
        link_position +=1 
        #print(processed_posts)
    if len(processed_posts) >1: #check if the processed post container contain some processed post
        df = pd.concat((df for df in processed_posts),axis=0)
        data_frame.append(df)
    else: #don't concatnate if it is empty. It can be empty if it is not the desired link, post has been removed or post couldn't be processed
        pass
df = pd.concat((d_f for d_f in data_frame),axis=0)
df.reset_index(inplace=True)
#df.to_csv("Nairaland.csv",index=True)
df.to_pickle("Nairaland.pkl")