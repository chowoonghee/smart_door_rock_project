import smtplib
from email.mime.text import MIMEText
import random

random_list = ['1','2','3','4','5','6','7','8','9','0','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w',
               'x','y','z','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W',
               'X','Y','Z','조웅희짱짱맨']
choice_list = random.choice(random_list)

def randomCode(num) :
    random_code = ""
    if num == 1 :
        for i in range(len(random_list)):
            num = random.choice(random_list)

            if num == "조웅희짱짱맨":
                random_code = "조웅희짱짱맨"
                break

            random_code += num

            if len(random_code) == 8:
                break

        return random_code

def check_email(name,email,code) :
    smtp = smtplib.SMTP('smtp.gmail.com',587)
    smtp.ehlo()
    smtp.starttls()
    smtp.login('son2257@gmail.com','cjpucafjglaeedow')

    msg = MIMEText(f"""안녕하세요. {name}님 !
스마트 도어락의 새로운 가족이 되신걸 진심으로 환영합니다.
안전한 서비스를 위하여 아래 인증 코드를 입력해주시기 바랍니다.

{code}""")
    msg['Subject'] = "스마트 도어락 인증 코드입니다."
    msg['To'] = f'{email}'
    smtp.sendmail('son2257@gmail.com',f'{email}',msg.as_string())

    print("메일전송완료")

    smtp.quit()