# Dependencies
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import requests
import io
import numpy as np
import pandas as pd

# Get the driver
driver = webdriver.Chrome("/usr/local/bin/chromedriver")

HotelsUrls = {'Newport_Bay_Club' : 'https://www.booking.com/hotel/fr/disney-39-s-newport-bay-club-r.fr.html#tab-reviews', 'Cheyenne' : 'https://www.booking.com/hotel/fr/disney-39-s-cheyenne-r.fr.html#tab-reviews', 'Sequoia_Lodge' : 'https://www.booking.com/hotel/fr/disneys-sequoia-lodge-r.fr.html#tab-reviews', 'New_York' : 'https://www.booking.com/hotel/fr/disney-39-s-new-york-r.fr.html#tab-reviews', 'Davy_Crockett_Ranch' : 'https://www.booking.com/hotel/fr/disneys-davy-crockett-ranch.fr.html#tab-reviews', 'Santa_Fe' : 'https://www.booking.com/hotel/fr/disney-39-s-santa-fe-r.fr.html#tab-reviews'}

# Create list to get the data
collectName = []
collectCountry = []
collectType_room = []
collectLen_reservation = []
collectMonth_year = []
collectVoyageur_info = []
collectDate_review = []
collectReview_title = []
collectGrade_review = []
collectPositive_review = []
collectNegative_review = []
collectIs_review_usefull = []
collectUniqueID = []

chiffres = list("0123456789")

for i in range(len(HotelsUrls)) : 

    git = 'https://github.com/paulineattal/Disney-Text-Mining/blob/main/fichiers/Scrapping_' + str(list(HotelsUrls.keys())[i]) + '.csv'
    link = git.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
    try : 
        checkUrl = requests.get(link).content
        checkScrapping = pd.read_csv(io.StringIO(checkUrl.decode('utf-8')), sep = ';')
    except : 
        pass 

    url = HotelsUrls.get(list(HotelsUrls.keys())[i])

    # Put the url into the driver
    driver.get(url)

    time.sleep(2)
    # Reject cookies
    driver.find_element(By.ID, "onetrust-reject-all-handler").click()

    driver.find_element(By.XPATH, '//*[@id="review_sort"]/option[2]').click()
    time.sleep(2)

    n_pages = driver.find_element(By.XPATH, '//*[@id="review_list_page_container"]/div[4]/div/div[1]/div/div[2]/div/div[7]/a/span[1]').text
    n_pages = int(n_pages)
    
    check = False
    if check == False : 

        for p in range(1,n_pages+1):
    
            time.sleep(2)

            for i in range(1,11):
        
                time.sleep(1)

                # Nom voyageur
                name_path = '//*[@id="review_list_page_container"]/ul/li['+str(i)+']/div/div[2]/div[1]/div[1]/div/div[2]/span[1]'
                try:
                    name = driver.find_element(By.XPATH, name_path).text
                except:
                    name = "empty"
                collectName.append(name)

                # Pays voyageur
                country_path = '//*[@id="review_list_page_container"]/ul/li['+str(i)+']/div/div[2]/div[1]/div[1]/div/div[2]/span[2]'
                try:
                    country = driver.find_element(By.XPATH, country_path).text
                except:
                    country = "empty"
                collectCountry.append(country)

                # Type de chambre
                type_room_path = '//*[@id="review_list_page_container"]/ul/li['+str(i)+']/div/div[2]/div[1]/div[2]/ul/li/a'
        
                try: 
                    type_room = driver.find_element(By.XPATH, type_room_path).text
                except:
                    type_room = "empty"
                collectType_room.append(type_room)

            # Nuitées
                len_reservation_path = '//*[@id="review_list_page_container"]/ul/li['+str(i)+']/div/div[2]/div[1]/ul[1]/li/div'
                try:
                    len_reservation = driver.find_element(By.XPATH, len_reservation_path).text
                except:
                    len_reservation = "empty"
                collectLen_reservation.append(len_reservation[0])

                # Mois année du voyage
                month_year_path = '//*[@id="review_list_page_container"]/ul/li['+str(i)+']/div/div[2]/div[1]/ul[1]/li/div/span'
                try:
                    month_year = driver.find_element(By.XPATH, month_year_path).text
                except:
                    month_year = "empty"
                collectMonth_year.append(month_year)

                # Informations voyageur
                voyageur_info_path = '//*[@id="review_list_page_container"]/ul/li['+str(i)+']/div/div[2]/div[1]/ul[2]/li'
                try:
                    voyageur_info = driver.find_element(By.XPATH, voyageur_info_path).text
                except:
                    voyageur_info = "empty"
                collectVoyageur_info.append(voyageur_info)

                # Date 
                date_review_path = '//*[@id="review_list_page_container"]/ul/li['+str(i)+']/div/div[2]/div[2]/div[1]/span'
                date_review_path2 = '//*[@id="review_list_page_container"]/ul/li['+str(i)+']/div/div[2]/div[2]/div[1]/span[2]'

                try:
                    date_review = driver.find_element(By.XPATH, date_review_path).text
                except:
                    date_review = "empty"

                if date_review == 'Le choix des voyageurs' : 
        
                    try:
                        date_review = driver.find_element(By.XPATH, date_review_path2).text
                    except:
                        date_review = "empty"
                collectDate_review.append(date_review)

                # Titre commentaire 
                review_title_path = '//*[@id="review_list_page_container"]/ul/li['+str(i)+']/div/div[2]/div[2]/div[1]/div/div[1]/h3'
                try:
                    review_title = driver.find_element(By.XPATH, review_title_path).text
                except:
                    review_title = "empty"
                collectReview_title.append(review_title)
        
                # Note
                grade_review_path = '//*[@id="review_list_page_container"]/ul/li['+str(i)+']/div/div[2]/div[2]/div[1]/div/div[2]/div/div'
                try:
                    grade_review = driver.find_element(By.XPATH, grade_review_path).text
                except:
                    grade_review = "empty"
                collectGrade_review.append(grade_review)

                # Commentaire positif
                positive_review_path = '//*[@id="review_list_page_container"]/ul/li['+str(i)+']/div/div[2]/div[2]/div[2]/div/div[1]/p/span[3]'
                try:
                    positive_review = driver.find_element(By.XPATH, positive_review_path).text
                except: 
                    positive_review = "empty"
                collectPositive_review.append(positive_review)
        
                # Commentaire négatif
                negative_review_path = '//*[@id="review_list_page_container"]/ul/li['+str(i)+']/div/div[2]/div[2]/div[2]/div/div[2]/p/span[3]'
                try:
                    negative_review = driver.find_element(By.XPATH, negative_review_path).text
                except:
                    negative_review = "empty"
                collectNegative_review.append(negative_review)

                # Utilité commentaire
                is_review_usefull_path = '//*[@id="review_list_page_container"]/ul/li['+str(i)+']/div/div[2]/div[2]/div[3]/div/div[1]'
                try:
                    is_review_usefull = driver.find_element(By.XPATH, is_review_usefull_path).text
                except:
                    is_review_usefull = "empty"
                collectIs_review_usefull.append(is_review_usefull)

                UniqueID = name + country + type_room + month_year + voyageur_info + date_review + review_title
                try: 
                    check = checkScrapping['UniqueID'].isin(UniqueID)
                except: 
                    check = False

                collectUniqueID.append(UniqueID)
        
            # Changer de page    
            try:
                driver.find_element(By.CLASS_NAME, "pagenext").click()     
            except:
                pass
    
        # Fermer le driver une fois 
        driver.close()
    else : 
        driver.close()
        break

    # Placer toute la donnée stockée
    Names = collectName
    Country = collectCountry
    room_type = collectType_room
    nuitee = collectLen_reservation
    reservation_date = collectMonth_year
    traveler_infos = collectVoyageur_info
    date_review = collectDate_review
    review_title = collectReview_title
    grade_review = collectGrade_review
    positive_review = collectPositive_review
    negative_review = collectNegative_review
    usefulness_review = collectIs_review_usefull
    UniqueID = collectUniqueID
    columns = ['Names', 'Country', 'room_type', 'nuitee', 'reservation_date', 'traveler_infos', 'date_review', 'review_title', 'grade_review', 'positive_review', 'negative_review', 'usefulness_review', 'UniqueID']

    # Créer le dataframe
    df = pd.DataFrame(list(zip(Names, Country,room_type, nuitee, reservation_date, traveler_infos, date_review, review_title, grade_review, positive_review, negative_review, usefulness_review, UniqueID)), columns=columns)
   
    # Assigner le nom de l'hôtel 
    df=df.assign(hotel= str(list(HotelsUrls.keys())[i]))

    # Garder le nombre de fois que le commentaire a été classé utile
    df.loc[(df.usefulness_review == 'Utile Pas utile'),'usefulness_review']='NaN'
    df['usefulness_review'] = df['usefulness_review'].str[:2]

    # Si pas d'avis, remplacer par 0
    for i in range(len(df)): 

        if df['usefulness_review'][i] == "em":
            df['usefulness_review'][i] = 0

        if df['usefulness_review'][i] is None:
            df['usefulness_review'][i] = 0

    # Supprimer les doublons
    df.drop_duplicates(keep='first')

    # Enregistrer en local, a changer dans le futur
    df.to_csv(r'C:\Users\houde\Documents\GitHub\Disney-Text-Mining\Scrapping\Scrapping_' + str(list(HotelsUrls.keys())[i]) + '.csv', index = False, sep=';', encoding='utf-8')