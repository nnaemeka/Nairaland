import time
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import requests
import numpy as np
import datetime
import pickle

def get_total_comments_by_text_slicing(text,topic):
    #total_comments includes the post itself
    split_comments = [i for i in text.split(topic)]
    j = 0
    total_comments = 0
    for i in split_comments:
        if j>3 and i.split()[0] == "by": #first four is always not comment, so ignore.
            #print(i)
            total_comments+=1
        j+=1
    return(total_comments)

def get_number_of_pages(site):
    #site = a['href']
    for i in range(10000):
    #print(i)
        if i == 0:
            req = requests.get(site)
            soup = BeautifulSoup(req.text, 'html.parser')
            title1 = soup.title.text        
        else:
            req = requests.get(site+"/"+str(i))
            soup = BeautifulSoup(req.text, 'html.parser')
            title2 = soup.title.text
            #print(site+"/"+str(i))
            if title1 == title2:
                break
            else:
                title1 = title2
    print("Number of pages are:",i)
    return(i)

def get_username_gender_shares_and_likes(text,topic,number_of_comments_by_tags_extraction):
    Likes = []
    Shares = []
    Username = []
    Gender = []
    comment_list = text.split(topic)
    number_of_comments_by_text_splitting = get_total_comments_by_text_slicing(text,topic)
    if number_of_comments_by_text_splitting == number_of_comments_by_tags_extraction:
        i=0 #for marking which splited pieces we are. First four are not comments
        for line in comment_list:
            #print(line)
            if len(line.split())>1 and i>3 and line.split()[0] == "by":
                if comment_list.index(line) == len(comment_list)-1:
                    likes,shares = get_last_comment_likes_and_shares(line)
                    Shares.append(shares)
                    Likes.append(likes)
                    username_gender = line.split()[1]
                    username,gender = get_user(username_gender)
                    Username.append(username)
                    Gender.append(gender)
                    #print("Likes***:",likes,"Shares:",shares,"Username:",username,"Gender:",gender)
                else:
                    likes_and_share = line.split()[-5:]
                    likes,shares = get_likes_and_share(likes_and_share)
                    Shares.append(shares)
                    Likes.append(likes)
                    username_gender = line.split()[1]
                    username,gender = get_user(username_gender)
                    Username.append(username)
                    Gender.append(gender)
            i+=1
    else: 
        correct_topic = topic[:-1] #removes the extra space at the end which is the cause.
        i=0 #for marking which splited pieces we are. First four are not comments
        comment_list = text.split(correct_topic)
        number_of_comments_by_text_splitting = get_total_comments_by_text_slicing(text,correct_topic)
        for line in comment_list:
            if len(line.split())>1 and i>3 and line.split()[0] == "by":
            #correct_length = len(comment_list)-4 #first four not comments
                if comment_list.index(line) == len(comment_list)-1: # checks if it is the last comment.
                    #print("Last comment")
                    likes,shares = get_last_comment_likes_and_shares(line)
                    Shares.append(shares)
                    Likes.append(likes)
                    username_gender = line.split()[1]
                    username,gender = get_user(username_gender)
                    Username.append(username)
                    Gender.append(gender)
                    #print("Likes:",likes,"Shares:",shares,"Username:",username,"Gender:",gender)
                else:
                    likes_and_share = line.split()[-5:]
                    likes,shares = get_likes_and_share(likes_and_share)
                    Shares.append(shares)
                    Likes.append(likes)
                    username_gender = line.split()[1]
                    username,gender = get_user(username_gender)
                    Username.append(username)
                    Gender.append(gender)
                    #print("Likes#####:",likes,"Shares:",shares,"Username:",username,"Gender:",gender)
                    #print("VERIFY:",number_of_comments_by_tags_extraction,correct_length)
            i+=1           
    return(Username,Gender,Shares,Likes,number_of_comments_by_text_splitting)

def get_last_comment_likes_and_shares(line):
    if len(line.split("Like")) > 1:
        last_comment_line = line.split("Like")[0]
        likes = last_comment_line.split()[-1]
        #print("Last Comment Likes",likes)
    else:
        likes = 0
    if len(line.split("Share")) > 1:
        last_comment_line = line.split("Share")[0]
        shares = last_comment_line.split()[-1]
        #print(" Last comment Shares",shares)
    else:
        shares = 0
    return(likes, shares)

def get_user(username_gender):
    split_username_gender = username_gender.split("(")
    username = username_gender.split("(")[0]
    if len(split_username_gender)==1:
        gender = None
    else:
        gender = split_username_gender[1].split(")")[0]
    return(username,gender)

def get_likes_and_share(likes_and_share):
    if likes_and_share[-1] == "Re:":
        pass
    if likes_and_share[-1] in ["ShareRe:","SharesRe:"]:
        likes_and_share[-1] = likes_and_share[-1][:-3]
    if likes_and_share[-1] in ["LikeRe:","LikesRe:"]:
        likes_and_share[-1] = likes_and_share[-1][:-3]
    for entry in likes_and_share:
        if entry in ["Like","Likes"]:
            likes = likes_and_share[likes_and_share.index(entry)-1]
            break
        else:
            likes = 0
    for entry in likes_and_share:
        if entry in ["Share","Shares"]:
            shares = likes_and_share[likes_and_share.index(entry)-1]
            break
        else:
            shares = 0
    return(likes,shares)

def get_comments(soup):
    title = soup.title.string
    topic = '-'.join(title.split("-")[:-2])
    section = title.split("-")[-2]
    comments = []
    k=0
    for link in soup.find_all('div',{'class':'narrow'}):
        comments.append(link.text)
        k+=1
    return(comments)

def is_number(value):
    '''
    Type-casting the string to `float`.
    If string is not a valid `float`, 
    it'll raise `ValueError` exception
    '''
    try:
        int(value)
    except ValueError:
        return False
    return True

def get_date(soup):
    #finds the date
    date = []
    j=0
    for link in soup.find_all('span',{'class':'s'}):
        date_components = []
        for i in range(len(link.find_all('b'))):
            time = link.find_all('b')[i].text
            date_components.append(time)
        full_date = format_date(date_components)
        date.append(full_date)
        j+=1
    return(date)

def format_date(date):
    today_date = datetime.datetime.now()
    today_month = today_date.strftime("%b")
    today_month_day = today_date.strftime("%d")
    today_year = today_date.strftime("%Y")
    if len(date) == 1:
        date_time = date[0]+" "+today_month+" "+today_month_day+" "+today_year
        return(date_time)
    if len(date) == 2:
        date_time = date[0]+" "+date[1]+" "+today_year
        return(date_time)
    else:
        return(date)
    return(0)
    
def get_post_features(username,gender,date,topic,author,section,country,comment,likes,shares):
    post_features = []
    #print("AUTHOR:",author)
    #time.sleep(10)
    b =1
    for i,j,k,l,m,n in zip(username,gender,date,comment,likes,shares):
        if b ==1 and author == "Yes":
            post_features.append([i,j,k,topic,author,section,country,l,m,n])
        else: #For comments following the post or comments in subsequent pages
            author = "No"
            post_features.append([i,j,k,topic,author,section,country,l,m,n])
        b+=1
        
    return(post_features)

def save_processed_posts(df,sites):
    with open('nairaland_dfs', 'wb') as fp:
        pickle.dump(df, fp)
    with open('visited_sites','wb') as f:
        pickle.dump(sites,f)
    return(0)

def load_processed_posts():
    try:
        with open ('nairaland_dfs', 'rb') as fp:
            dfs = pickle.load(fp)
    except:
        dfs = []
        print("the file for processed posts is not created yet")
    return(dfs)

def load_processed_sites():
    try:
        with open ('visited_sites', 'rb') as f:
            sites = pickle.load(f)
    except:
        sites = []
        print("the file for proccessed sites is not created yet")
    return(sites)

def save_bad_sites(sites):
    with open('Bad_sites','wb') as f:
        pickle.dump(sites,f)
    return(0)

def load_bad_sites():
    try:
        with open ('Bad_sites', 'rb') as f:
            bad_sites = pickle.load(f)
    except:
        bad_sites = []
    return(bad_sites)