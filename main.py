import requests
from bs4 import BeautifulSoup
from fake_headers import Headers
from tqdm import tqdm
import os
import re
import json

def headers_gen():
    return Headers(browser="chrome", os="win").generate()

def main_hh(url):
    main_page = requests.get(url=url, headers=headers_gen()).text
    soup_page = BeautifulSoup(main_page, "lxml")
    common_vac_tag = soup_page.find_all("div", class_="serp-item")
    return common_vac_tag

def hh_work_search(tag_vacancy):
    job_link = tag_vacancy.find("a", class_="serp-item__title")["href"]
    if tag_vacancy.find("span", class_="bloko-header-section-3") == None:
        employee_salary = f"Информация по зарплате отсутствует"
    else:
        employee_salary = tag_vacancy.find("span", class_="bloko-header-section-3").text
    company_vacancy = tag_vacancy.find(
        "a", "bloko-link bloko-link_kind-tertiary"
    ).text
    vacancy_city = tag_vacancy.find(
        attrs={"data-qa": "vacancy-serp__vacancy-address"}
    ).text
    description_tag = requests.get(url=job_link, headers=headers_gen()).text
    description_tag_soup = BeautifulSoup(description_tag, "lxml")
    job_description = description_tag_soup.find("div", class_="g-user-content").text

    return {
        "link": job_link,
        "salary": employee_salary,
        "name_company": company_vacancy,
        "city": vacancy_city,
        "description": job_description
    }

def request_search(home_page):
    final_list = []
    for tag_vacancy in tqdm(home_page):
        find_vacancy = hh_work_search(tag_vacancy)
        job_specs = find_vacancy["description"]
        pattern = re.findall(
            r"([Dd]jango.*[Ff]lask)|([Ff]lask.*[Dd]jango)|([Ff]lask.*\s*.*[Dd]jango)",
            job_specs,
        )
        if pattern != []:
            _ = find_vacancy.pop("description", None)
            final_list.append(find_vacancy)
    return final_list

def file_write(folder_name, file_name, final_list):
    actual = os.getcwd()
    full_path = os.path.join(actual, folder_name, file_name)
    with open(full_path, "w", encoding="utf=8") as f:
        json.dump(final_list, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    home_page = main_hh(
        "https://spb.hh.ru/search/vacancy?text=python&area=1&area=2"
    )
    final_result = request_search(home_page)
    file_write("HH Scrapping", "job_results.json", final_result)