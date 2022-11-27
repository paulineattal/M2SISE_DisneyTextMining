# -*- coding: utf-8 -*-
"""
Created on Tue Nov 22 16:27:20 2022

@author: pauli
"""

from selenium import webdriver
from bs4 import BeautifulSoup


driver = webdriver.Firefox()
#Chrome("/home/pauline/chromedriver_linux64/chromedriver")

url = "https://www.booking.com/hotel/fr/disneys-davy-crockett-ranch.fr.html?aid=311089&label=disneys-davy-crockett-ranch-zsqKbcBAJlS%2AWXn0gGobRAS579525560861%3Apl%3Ata%3Ap1%3Ap2%3Aac%3Aap%3Aneg%3Afi%3Atikwd-398254433747%3Alp9055470%3Ali%3Adec%3Adm%3Appccp%3DUmFuZG9tSVYkc2RlIyh9YVujEjbMrKBV7ahOy8HtCLg&sid=12a96f6c9ee76028b5dcd41f8ea778f9&dest_id=-1476944;dest_type=city;dist=0;group_adults=2;group_children=0;hapos=1;hpos=1;no_rooms=1;req_adults=2;req_children=0;room1=A%2CA;sb_price_type=total;sr_order=popularity;srepoch=1669130533;srpvid=4b326c12facc00a8;type=total;ucfs=1&#hotelTmpl"
url="https://www.booking.com/hotel/fr/disneys-davy-crockett-ranch.fr.html?aid=311089&label=disneys-davy-crockett-ranch-zsqKbcBAJlS%2AWXn0gGobRAS579525560861%3Apl%3Ata%3Ap1%3Ap2%3Aac%3Aap%3Aneg%3Afi%3Atikwd-398254433747%3Alp9055470%3Ali%3Adec%3Adm%3Appccp%3DUmFuZG9tSVYkc2RlIyh9YVujEjbMrKBV7ahOy8HtCLg&sid=d5171b695f32e31b9238a3e4afbde9f8&dest_id=-1476944;dest_type=city;dist=0;group_adults=2;group_children=0;hapos=1;hpos=1;no_rooms=1;req_adults=2;req_children=0;room1=A%2CA;sb_price_type=total;sr_order=popularity;srepoch=1669577571;srpvid=2ea98971ea470094;type=total;ucfs=1&#tab-reviews"
driver.get(url)

response = BeautifulSoup(driver.page_source, 'html.parser')
r = response.find_all('li', class_="review_list_new_item_block")


rev_dict = {'Review Text': [],
            'Review Name' : [],
            'Review Time': [],
            'Review Perso Num Rate' : [],
            'Review Rate' : []}

for rv in r :
    print(rv)
    
    #review_text = rv.find_all('span', class_='')
    #review_name = rv.find_all('span', jstcache='304')
    #review_date = rv.find_all('span',class_='')
    #review_perso_num_rate = rv.find_all('span', jstcache='324') 
    #review_rate = rv.find_all('span', class_="")
    

