import requests
from bs4 import BeautifulSoup

import urllib
import json
from datetime import datetime

# all-events, events--tomorrow, events--this-week, events--next-week, events--this-month, events--next-month, events--this-weekend, events--today, events--this-weekend
# For pick date use second param &start_date=2020-01-28&end_date=2020-01-31 and period = all-events
# eg. https://www.eventbrite.com/d/cityOrCountry/all-events/?page=1&start_date=2050-12-01&end_date=2050-12-31
period = 'events--next-month'
# Cuantas paginas serán analizadas
pageLimit = 2
# Cual es la pagina incial a analizar
pageInit = 1
# Cuales paises o ciudades se analizaran
countries = ['mexico', 'colombia']


dataContainer = []


def run():
    print('Proceso iniciado {}'.format(
        datetime.now().strftime('%b %dth, %Y - %H:%M hrs')))

    for country in countries:
        print('Analizando enlaces de {}, espere por favor'.format(country))
        for page in range(pageInit, pageLimit + 1):
            response = requests.get(
                'https://www.eventbrite.com/d/{}/{}/?page={}'
                .format(country, period, page)
            )
            soup = BeautifulSoup(response.content, 'html.parser')
            link_container = soup.findAll(
                "div", {"class": "eds-media-card-content__primary-content"}
            )

            dataContainer.extend(list(
                map(lambda link: link.find('a')['href'], link_container)
            ))

    dataContainerClear = dict.fromkeys(dataContainer)

    print('Se analizaron los enlaces de {} paises'.format(len(countries)))
    print('Se iniciaza el análisis de {} eventos encontrados'.format(
        len(dataContainerClear)))

    flag = 0
    obtainData = 0
    dateFile = datetime.now()
    bitacora = open("result/bitacora_{}.txt".format(dateFile), "w")

    with open("result/data_{}.json".format(dateFile), "w", encoding='utf-8') as outfile:
        for url in dataContainerClear:
            flag += 1
            print('{} - Analizando evento {}'.format(
                flag,
                url.split('/')[-1].replace('?aff=ebdssbdestsearch', '')), end=" ")
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            dataCont = str(soup.find("script", type="application/ld+json"))
            if (dataCont):
                try:
                    data = dataCont.replace(
                        '<script type="application/ld+json">', '')
                    data = data.replace('</script>', '')
                    data = data.encode('utf-8')
                    json_object = json.dumps(json.loads(data), indent=4)
                    outfile.write(json_object)
                    outfile.write(',\n')
                    obtainData += 1
                    print("(ok)")
                    bitacora.write(
                        '{} - {} (ok)'.format(
                            flag,
                            url.split(
                                '/')[-1].replace('?aff=ebdssbdestsearch', '')
                        )
                    )
                except ValueError as e:
                    print("(error)")
                    bitacora.write(
                        '{} - {} (error) {}'.format(
                            flag,
                            url.split(
                                '/')[-1].replace('?aff=ebdssbdestsearch', ''),
                            url
                        )
                    )
                    pass

                bitacora.write('\n')
                # return

    outfile.close()
    bitacora.close()

    print("Resultados obtenidos: {}".format(obtainData))
    print('Proceso finalizado {}'.format(
        datetime.now().strftime('%b %dth, %Y - %H:%M hrs')))


if __name__ == '__main__':
    run()
