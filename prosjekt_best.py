# -*- coding: utf-8 -*-

#Oppgave 4: Aksjeoppgave
#Programert av Aksel, Nicolai og Marcus

# Importerer nødvendige biblioteker:
import requests
import matplotlib.pyplot as plt
import json
import datetime as dt
import numpy as np

#Definerer variabler
today = dt.date.today()#Henter dagens dato fra datetime
api_key = "a54d48bd0d164e0299784bfc541b56b9" # Api-kode fra twelve data, personlig

# Tar inn antall aksjer brukeren vil analysere, og sjekker om det er godkjent
while True:
  amount = input("Ønsker du å analysere 1 eller 2 aksjer? ").upper()

  if amount == "EN":
      amount = 1
  elif amount == "TO":
      amount = 2
  elif amount == "1" or amount == "2":
      amount = int(amount)

  if amount == 1 or amount == 2:
    break
  else:
    print("Du må velge enten 1 eller 2 aksjer! Prøv igjen.")



# Spør hvor lang tidshorisont brukeren har for sparingen, og sjekker om det er godkjent
while True:
    savingPeriod = input("Ønsker du å spare på kort eller lang sikt? ").lower()

    if savingPeriod == "lang sikt" or savingPeriod == "lang":
        recommendation1 = 50
        recommendation2 = 200
        break
    elif savingPeriod == "kort sikt" or savingPeriod == "kort":
        recommendation1 = 10
        recommendation2 = 50
        break
    else:
        print("Du må velge enten kort eller lang sikt.")

#Sjekker om stock eksisterer på APIet
#Dette gjøres ved at vi sjekker om det finnes data i stock,  altså om mengden data er større enn 1
def is_stock_valid(stock):
    url = f"https://api.twelvedata.com/stocks?symbol={stock}"
    response = requests.get(url).json()
    return len(response["data"]) >= 1


companies = [] # Tom liste som skal fylles med selskap

# Henter selskaper brukeren vil se på, legger til i companies hvis det fins
while len(companies) < amount:
    stock = input("Hvilken NASDAQ-notert aksje vil du se på? Skriv inn akjsesymbol: ").upper()

   #Sjekker om aksjen er valid
    if is_stock_valid(stock):
        companies.append(stock)
    else:
        print("Aksjen eksisterer ikke, eller er ikke notert på NASDAQ.")

# Setter en grense for hvor mange dager tilbake man kan se og sjekker om days er et gyldig heltall mellom 1 - 1000
def is_days_valid(days):
    return type(days) == int and days in range(1, 1000 + 1)

#Brukeren vil motta spørsmålet og ikke komme videre i programmet så lenge input ikke er godkjent
#Løkken breaker når "days" er godkjent
while True:
    daysByUser = int(input("For hvor mange dager tilbake vil du se kurs? (1-1000): "))
    if is_days_valid(daysByUser):
        break


daysForAverage = daysByUser # daysForAverage skal brukes til gjennomsnitt, daysByUser til plotting

# Bestemmer hvor ofte vi vil se dataene
if daysByUser <= 50:
    interval = "4h"
    daysByUser = daysByUser*2
else:
    interval = "1day"


def get_stock_history(ticker_symbol, api, date, plotNum, interval):
  url = f"https://api.twelvedata.com/time_series?end_date={date}&outputsize={plotNum}&symbol={ticker_symbol}&interval={interval}&apikey={api}"

  response = requests.get(url).json()
  return response

def average(averageDays):
    sum = 0
    stock_history = get_stock_history(stock, api_key, today, averageDays, interval)
    values = stock_history["values"]
    for i in range(len(values)):
        sum += float(values[i]["close"]) # Bruker "close"-verdien, når børsen stenger

    return round(sum / len(values))

# Bestemmer om vi anbefaler aksjen basert på gjennomsnittet siste 10 eller 50 dager opp mot siste 50 eller 200
def recommendation(pastHistoricDays1, pastHistoricDays2, stock):
    rec1 = average(pastHistoricDays1)
    rec2 = average(pastHistoricDays2)
    recommend = f"\nFor {stock} eller {name}. Gjennomsnittet de siste {pastHistoricDays1} dagene er {rec1} {currency}. Det er høyere enn gjennomsnittet de siste {pastHistoricDays2} dagene, som er på {rec2} {currency}. Dette tilsier enn stigende graf. Vi anbefaler å kjøpe aksjen."
    dont_recommend = f"\nFor {stock} eller {name}. Gjennomsnittet de siste {pastHistoricDays1} dagene er {rec1} {currency}. Det er lavere enn gjennomsnittet de siste {pastHistoricDays2} dagene, som er på {rec2} {currency}. Dette tilsier enn synkende graf. Vi anbefaler ikke å kjøpe aksjen."


    #Returner vår anbefaling basert på  close-verdine i forhold til antall dager 
    if rec1 > rec2:
        return recommend
    elif rec1 < rec2:
        return dont_recommend
    else:
        return "Gjennomsnittet er likt for begge periodene. vi gir derfor ingen anbefaling."

# Funksjon for y-verdiene til regresjon
def linRegresjon(x, y):
    reg = np.polyfit(x, y, 1)
    x_array = np.array(x)
    regression = (reg[0] * x_array + reg[1]).tolist()
    return regression

# Finner info og plotter for alle elementer i companies
for i in range(len(companies)):
    prices = []
    dates = []

    stock = companies[i]

  # Henter info om aksjen. Values er en liste, inneholder info om hvert enkelt tidspunkt.
    stock_history = get_stock_history(stock, api_key, today, daysByUser, interval)
    values = stock_history["values"]

    # Legger til pris og dato for hvert tidspunkt
    for i in range(len(values)):
        price = float(values[i]["close"])
        prices.append(price)

        date = values[i]["datetime"]

        # Endrer tiden til datetime
        if interval == "1day":
            date = dt.datetime.strptime(date,"%Y-%m-%d")
        elif interval == "4h":
            date = dt.datetime.strptime(date,"%Y-%m-%d %H:%M:%S")

        dates.append(date)

    # Reverserer listene slik at de plottes i riktig rekkefølge
    dates = dates[::-1]
    prices = prices[::-1]
    currency = stock_history["meta"]["currency"] #Finner valutaen

  #Henter navnet til aksjen, brukes i title på grafen
    stock_name = f"https://api.twelvedata.com/stocks?symbol={stock}"
    response = requests.get(stock_name).json()
    name = response["data"][0]["name"]


    #Plotter verdiene til grafen:

    plt.plot(dates, prices, "green", linestyle=":", label="Aksjekurs")

    # Gjør listen som skal brukes til regresjonen om til array
    priceReg = np.array(prices)

    # Finner verdiene som skal plottes til regresjonen
    startdate = min(dates)  
    numeric_dates = [(date - startdate).days for date in dates]
    regression = linRegresjon(numeric_dates, priceReg)


    # Plotter regresjon
    plt.plot(dates, regression, "red", label = "Regresjon kurs")

    #Gjør alt pent:
    plt.gcf().autofmt_xdate()

    plt.title(f"Kursdata for {name}")
    plt.xlabel("Dato")
    plt.ylabel(f"Kurs ({currency})")

    plt.rc("xtick", labelsize=10)
    plt.rc("ytick", labelsize=12)
    plt.rc("axes", titlesize=12)
    plt.rc("figure", titlesize=14)

    plt.legend()
    plt.grid()
    plt.show()

    # Printer kjøpsanbefalingen 
    print(recommendation(recommendation1,recommendation2, stock))