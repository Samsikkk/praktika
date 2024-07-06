import requests
import json
import copy


def getAreas():
    req = requests.get('https://api.hh.ru/areas')
    data = req.content.decode()
    req.close()
    jsObj = json.loads(data)
    areas = []
    for k in jsObj:
        for i in range(len(k['areas'])):
            if len(k['areas'][i]['areas']) != 0:
                for j in range(len(k['areas'][i]['areas'])):
                    areas.append([k['areas'][i]['areas'][j]['id'],
                                  k['areas'][i]['areas'][j]['name']])
            else:
                areas.append([k['areas'][i]['id'],
                              k['areas'][i]['name']])
    return areas


areas = getAreas()


def getVacancies(keyword="Python Developer", area="", salary=0, cntVac=10) -> list:
    global areas
    buff = {
        "id": "",
        "name": "",
        "url": "",
        "metro": "",
        "salary": 0,
        "company": ""
    }
    areas.sort(key=lambda z: z[1] == area, reverse=True)
    area = areas[0][0]
    hhResponse = []
    url = "https://api.hh.ru/vacancies"
    params = {
        "text": keyword,
        "area": area,
        "per_page": cntVac,
    }
    headers = {
        "User-Agent": "Your User Agent",  # Replace with your User-Agent header
    }

    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        data = response.json()
        vacancies = data.get("items", [])
        for vacancy in vacancies:
            buff["id"] = vacancy.get("id")
            buff["name"] = vacancy.get("name")
            buff["url"] = vacancy.get("alternate_url")
            buff["company"] = vacancy.get("employer", {}).get("name")
            buff["salary"] = vacancy.get("salary")
            buff["metro"] = vacancy.get("metro")
            tmp = copy.deepcopy(buff)
            hhResponse.append(tmp)


        return hhResponse
    else:
        print(f"Ошибка в поиске ваканский. Error code -> {response.status_code}")


if __name__ == '__main__':
    print(getVacancies("python разработчик", "Москва"))