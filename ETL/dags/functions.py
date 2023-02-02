# Dependencies
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import numpy as np
import pandas as pd
import psycopg2
import psycopg2.extras as extras
import datetime

# Get the driver
HotelsUrls = {'Newport_Bay_Club' : 'https://www.booking.com/hotel/fr/disney-39-s-newport-bay-club-r.fr.html#tab-reviews', 'Cheyenne' : 'https://www.booking.com/hotel/fr/disney-39-s-cheyenne-r.fr.html#tab-reviews', 'Sequoia_Lodge' : 'https://www.booking.com/hotel/fr/disneys-sequoia-lodge-r.fr.html#tab-reviews', 'New_York' : 'https://www.booking.com/hotel/fr/disney-39-s-new-york-r.fr.html#tab-reviews', 'Davy_Crockett_Ranch' : 'https://www.booking.com/hotel/fr/disneys-davy-crockett-ranch.fr.html#tab-reviews', 'Santa_Fe' : 'https://www.booking.com/hotel/fr/disney-39-s-santa-fe-r.fr.html#tab-reviews'}
chiffres = list("0123456789")


#fonction qui va scraper les données a l'aide de la librairie Selenium
def scrapping_hotel(hotel, history):
        driver = webdriver.Chrome("/usr/local/bin/chromedriver")
        
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

        url = HotelsUrls.get(list(HotelsUrls.keys())[hotel])

        # Put the url into the driver
        driver.get(url)

        time.sleep(2)
        # Reject cookies
        driver.find_element(By.ID, "onetrust-reject-all-handler").click()

        driver.find_element(By.XPATH, '//*[@id="review_sort"]/option[2]').click()
        time.sleep(2)

        driver.find_element(By.CLASS_NAME, "pagenext").click()     

        # Récupérer le nombre de pages pour déterminer quand il faut s'arrêter
        time.sleep(1)

        # Initialiser le check à 0 qui servira si nous avons déjà l'information
        check = 0

        for p in range(1,150+1):
            time.sleep(2)
            print(p)

            if check == 0:

                for i in range(1,11):
                    
                    time.sleep(1)      
                    if check == 0 :
                        # Nom voyageur
                        name_path = '//*[@id="review_list_page_container"]/ul/li['+str(i)+']/div/div[2]/div[1]/div[1]/div/div[2]/span[1]'
                        try:
                            name = driver.find_element(By.XPATH, name_path).text
                        except:
                            name = np.nan
                        collectName.append(name)

                        # Pays voyageur
                        country_path = '//*[@id="review_list_page_container"]/ul/li['+str(i)+']/div/div[2]/div[1]/div[1]/div/div[2]/span[2]'
                        try:
                            country = driver.find_element(By.XPATH, country_path).text
                        except:
                            country = np.nan
                        collectCountry.append(country)

                        # Type de chambre
                        type_room_path = '//*[@id="review_list_page_container"]/ul/li['+str(i)+']/div/div[2]/div[1]/div[2]/ul/li/a'
            
                        try: 
                            type_room = driver.find_element(By.XPATH, type_room_path).text
                        except:
                            type_room = np.nan
                        collectType_room.append(type_room)

                        # Nuitées
                        len_reservation_path = '//*[@id="review_list_page_container"]/ul/li['+str(i)+']/div/div[2]/div[1]/ul[1]/li/div'
                        try:
                            len_reservation = driver.find_element(By.XPATH, len_reservation_path).text
                        except:
                            len_reservation = "N"
                        collectLen_reservation.append(len_reservation)

                        # Mois année du voyage
                        month_year_path = '//*[@id="review_list_page_container"]/ul/li['+str(i)+']/div/div[2]/div[1]/ul[1]/li/div/span'
                        try:
                            month_year = driver.find_element(By.XPATH, month_year_path).text
                        except:
                            month_year = np.nan
                        collectMonth_year.append(month_year)

                        # Informations voyageur
                        voyageur_info_path = '//*[@id="review_list_page_container"]/ul/li['+str(i)+']/div/div[2]/div[1]/ul[2]/li'
                        try:
                            voyageur_info = driver.find_element(By.XPATH, voyageur_info_path).text
                        except:
                            voyageur_info = np.nan
                        collectVoyageur_info.append(voyageur_info)

                        # Date 
                        date_review_path = '//*[@id="review_list_page_container"]/ul/li['+str(i)+']/div/div[2]/div[2]/div[1]/span'
                        date_review_path2 = '//*[@id="review_list_page_container"]/ul/li['+str(i)+']/div/div[2]/div[2]/div[1]/span[2]'

                        try:
                            date_review = driver.find_element(By.XPATH, date_review_path).text
                        except:
                            date_review = np.nan

                        # Supprimer le caractère le choix des voyageurs lorsqu'il est écrit
                        if date_review == 'Le choix des voyageurs' : 
            
                            try:
                                date_review = driver.find_element(By.XPATH, date_review_path2).text
                            except:
                                date_review = np.nan
                        collectDate_review.append(date_review)

                        # Titre commentaire 
                        review_title_path = '//*[@id="review_list_page_container"]/ul/li['+str(i)+']/div/div[2]/div[2]/div[1]/div/div[1]/h3'
                        try:
                            review_title = driver.find_element(By.XPATH, review_title_path).text
                        except:
                            review_title = np.nan
                        collectReview_title.append(review_title)
            
                        # Note
                        grade_review_path = '//*[@id="review_list_page_container"]/ul/li['+str(i)+']/div/div[2]/div[2]/div[1]/div/div[2]/div/div'
                        try:
                            grade_review = driver.find_element(By.XPATH, grade_review_path).text
                        except:
                            grade_review = np.nan
                        collectGrade_review.append(grade_review)

                        # Commentaire positif
                        positive_review_path = '//*[@id="review_list_page_container"]/ul/li['+str(i)+']/div/div[2]/div[2]/div[2]/div/div[1]/p/span[3]'
                        try:
                            positive_review = driver.find_element(By.XPATH, positive_review_path).text
                        except: 
                            positive_review = np.nan
                        collectPositive_review.append(positive_review)
            
                        # Commentaire négatif
                        negative_review_path = '//*[@id="review_list_page_container"]/ul/li['+str(i)+']/div/div[2]/div[2]/div[2]/div/div[2]/p/span[3]'
                        try:
                            negative_review = driver.find_element(By.XPATH, negative_review_path).text
                        except:
                            negative_review = np.nan
                        collectNegative_review.append(negative_review)

                        # Utilité commentaire
                        is_review_usefull_path = '//*[@id="review_list_page_container"]/ul/li['+str(i)+']/div/div[2]/div[2]/div[3]/div/div[1]'
                        try:
                            is_review_usefull = driver.find_element(By.XPATH, is_review_usefull_path).text
                        except:
                            is_review_usefull = np.nan
                        collectIs_review_usefull.append(is_review_usefull)

                        # Création d'un ID unique pour déterminer si nous avons déjà le commentaire ou non
                        UniqueID = str(name) + str(country) + str(type_room) + str(month_year) + str(voyageur_info) + str(date_review) + str(review_title)
                        
                        # Si nous avons un doublon, le check deviendra > 0 et le scrapping s'arrêtera
                        try: 
                            check = len(history[history['uniqueid'] == UniqueID])
                        except: 
                            check = 0
                    
                        collectUniqueID.append(UniqueID)
            
                # Changer de page    
                try:
                    driver.find_element(By.CLASS_NAME, "pagenext").click()     
                except:
                    pass
        
            else:
                break

        driver.close()
        
        # Créer le dataframe
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

        # Nom de colonnes
        columns = ['Names', 'Country', 'room_type', 'nuitee', 'reservation_date', 'traveler_infos', 'date_review', 'review_title', 'grade_review', 'positive_review', 'negative_review', 'usefulness_review', 'UniqueID']
        df = pd.DataFrame(list(zip(Names, Country,room_type, nuitee, reservation_date, traveler_infos, date_review, review_title, grade_review, positive_review, negative_review, usefulness_review, UniqueID)), columns=columns)
        df=df.assign(hotel= str(list(HotelsUrls.keys())[hotel]))
    
        # Traitement de la ligne usefulness_review : Garder uniquement le nombre de fois que le commentaire a été trouvé utile
        df.loc[(df.usefulness_review == 'Utile Pas utile'),'usefulness_review']= 'NaN'
        df['usefulness_review'] = df['usefulness_review'].str[:2]

        # Remplacer les cases ou il n'y a pas d'avis positif par 0
        df.loc[df.usefulness_review == "Na", "usefulness_review"] = "0"
        df.loc[pd.isna(df.usefulness_review), "usefulness_review"] = "0"

        # Remplacer les nuitees non complétées par np.nan
        df.loc[df.nuitee == "N", "nuitee"] = np.nan
        # Garder uniquement le nombre de nuitee passée dans l'hotel
        df["nuitee"] = df["nuitee"].str[:1]
        df["nuitee"] = df["nuitee"].fillna(0)
        # Supprimer les commentaires scrappés en trop (l'unique ID renvoie 'nannannannannannannan')
        df.drop(df[df['UniqueID'] == 'nannannannannannannan'].index, inplace = True)

        date = datetime.date.today()
        df = df.assign(execution_date= str(date))
        return df

#Fonction pour execter une requete req vers la connexion conn 
def execute_req(conn, req):
    try: 
        cursor = conn.cursor()
        cursor.execute(req)
        conn.commit()
        cursor.close()
    except (Exception, psycopg2.Error) as error :
        print ("Erreur lors de la création du table PostgreSQL", error)

#Fonction pour inserer des valeurs provenant un DataFrame df, dans la table table de la connexion conn
def insert_values(conn, df, table):
    tuples = [tuple(x) for x in df.to_numpy()]
    print("coucou")
    cols = ','.join(list(df.columns))
    print('bonjour')
    # SQL query to execute
    query = "INSERT INTO %s(%s) VALUES %%s" % (table, cols)
    print("oui")
    cursor = conn.cursor()
    try:
        extras.execute_values(cursor, query, tuples)
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Erreur: %s" % error)
        conn.rollback()
        cursor.close()
        return 1
    print("Le dataframe à été inseré")
    cursor.close()