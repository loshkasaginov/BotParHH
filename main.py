import requests
import telebot
from bs4 import BeautifulSoup

bot = telebot.TeleBot('')
All_list=[]
joker={}
HEADERS={
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'
}


##################################
places_dict = {
    'москва': 1,
    'санкт-петербург': 2,
    'екатеринбург': 3,
    'новосибирск': 4,
    'украина': 5,
    'австрия': 7,
    'майкоп': 8,
}
##################################
##

##


def Get_salary(salary):

    liste = salary.split()

    if liste[0].lower() == 'от' or liste[0].lower() == 'до':
        salary = int(liste[1]) * 1000
    else:
        salary = int(liste[0]) + int(liste[3])
        salary = int(salary) * 1000 / 2

    # Transfer from EUR or USD to RUB
    if liste[-1] == 'EUR':
        salary = float(salary) * 71

    elif liste[-1] == 'USD':
        salary = float(salary) * 63

    return float(salary)


#Get html naxuy stranitsu
def Get_html(url, params=''):
    r=requests.get(url,headers=HEADERS,params=params)
    return r

def Get_content(html,URL):
    session = requests.Session()
    req = session.get(URL, headers=HEADERS)
    soup=BeautifulSoup(req.content, 'html.parser')
    items= soup.find_all('div',attrs={"data-qa": "vacancy-serp__vacancy vacancy-serp__vacancy_standard_plus"})
    for item in items:
        try:
            title = item.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-title'}).text
            href = item.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-title'})['href']
            company = item.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-employer'}).text
            story=item.find(attrs={'data-qa': 'vacancy-serp__vacancy_snippet_responsibility'}).text
            salary = item.find(attrs={'data-qa': 'vacancy-serp__vacancy-compensation'}).text
            salary_Int=Get_salary(salary)
            All_list.append((salary_Int,title,href,company,story,salary))


        except:
            pass


def  Get_URL(place, job,num):
    return f"https://hh.ru/search/vacancy?search_period=5&clusters=true&area={places_dict[place]}&text={job}&page={num}"

def GetAvSalary(place,job,wanted_salary):
    for i in range(5):
        URL=Get_URL(place,job,i)
        html=Get_html(URL)
        if html.status_code==200:
            Get_content(html,URL)
    batman=sorting(wanted_salary)
    return batman

def sorting(wanted_salary):
    for i in range(len(All_list)):

        joker[All_list[i]]=abs(All_list[i][0]-wanted_salary)

    sorted_tuple = sorted(joker.items(), key=lambda x: x[1])
    return sorted_tuple


@bot.message_handler(content_types=['text'])

def start(message):
    global salary_list
    global All_list
    All_list = []
    salary_list=[]
    if message.text == '/start':
        bot.send_message(message.from_user.id, "Назовите профессию")
        bot.register_next_step_handler(message, get_job)
    else:
        bot.send_message(message.from_user.id, 'Напиши /start')

def get_job(message):
    global job
    job = message.text
    bot.send_message(message.from_user.id, 'Назовите город')
    bot.register_next_step_handler(message, get_place)
def get_place(message):
    global place
    global a
    a=True
    place = message.text
    place=place.lower()

    if place not in places_dict:
        bot.send_message(message.from_user.id, "этот город, к сожалению, пока недоступен"+'\n'+ "Если хотите ввести другой город, напишите:"+'\n'+'еще раз'+'\n'+"если хотите начать сначала, напишите:"+'\n'+'заного')
        bot.register_next_step_handler(message, proverka_Place)
    else:
        bot.send_message(message.from_user.id, "назовите желаемую зарплату ")
        bot.register_next_step_handler(message, get_wanted_salary)


def proverka_Place(message):
    mas=message.text
    mas=mas.lower()
    if mas == 'еще раз':
        bot.send_message(message.from_user.id, 'введите город заного: ')
        bot.register_next_step_handler(message, get_place)
    else:
        bot.register_next_step_handler(message, start)

def proverka_Salary(message):
    mas=message.text
    mas=mas.lower()
    if mas == 'еще раз':
        bot.send_message(message.from_user.id, 'назовите желаемую зарплату заного: ')
        bot.register_next_step_handler(message, get_wanted_salary)
    else:
        bot.register_next_step_handler(message, start)

def get_wanted_salary(message):
    global place, job, All_list
    try :
        wanted_salary = int(message.text)
        bot.send_message(message.from_user.id, "дайте подумать...")
        JobDict=GetAvSalary(place,job,wanted_salary)
        if len(JobDict)<3:
            bot.send_message(message.from_user.id, "такая профессия в данном городе не ликвидна")
            bot.register_next_step_handler(message, start)
        else:
            str1=JobDict[0][0][1]+ '\n'+ str(JobDict[0][0][5])+ '\n' +JobDict[0][0][2]+'\n'+JobDict[0][0][4]
            str2=JobDict[1][0][1]+ '\n'+ str(JobDict[1][0][5])+ '\n' +JobDict[1][0][2]+'\n'+JobDict[1][0][4]
            str3=JobDict[2][0][1]+ '\n'+ str(JobDict[2][0][5])+ '\n' +JobDict[2][0][2]+'\n'+JobDict[2][0][4]
            bot.send_message(message.from_user.id,str1)
            bot.send_message(message.from_user.id, str2)
            bot.send_message(message.from_user.id, str3)
            bot.register_next_step_handler(message, start)
    except:
        bot.send_message(message.from_user.id, "можете написать пожалуйста зарплату цифрами "+'\n'+ "Если хотите ввести другую зарплату напишите:"+'\n'+'еще раз'+'\n'+"если хотите начать сначала, напишите:"+'\n'+'заного')
        bot.register_next_step_handler(message, proverka_Salary)

if __name__=='__main__':
    bot.polling(none_stop=True, interval=0)
