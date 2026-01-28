

# 1728748800_000_000_000 (纳秒) ~ 2024-10-13 00:00:00
# 0 对应 1970-1-1 08:00:00
day_time = 24*60*60 # 单位：秒
days = [0,
        31,28,31,
        30,31,30,
        31,31,30,
        31,30,31
        ]



def is_leap_year(year):
    if(year%100 == 0 and year%400 != 0):
        return False
    return (year%4==0)

def year_time(year):
    return day_time * (365 + is_leap_year(year))




def in_year_time(year,month,day):
    # 从 year-1-1 00:00:00 至 year-month-day 00:00:00 的时间（单位：秒）
    sum = 0
    for m in range(1,month):
        sum += day_time * days[m]
    if(month > 2 and is_leap_year(year)):
        sum += day_time
    sum += day_time * (day-1)
    return sum
    
def is_valid_date(date:str)->bool:
    """
    输入必须满足 "YYYY-MM-DD"
    然后还要合法    
    """
    if len(date) != 10: return False
    if(date.count('-')!=2): return False
    if(date[4]!='-' or date[7]!='-'): return False
    try:
        year,month,day = map(int,date.split('-'))
        if(day==0 or month==0 or month>12 or year==0):return False
        if(month==2):
            return day<=(28+is_leap_year(year))
        return day<=days[month]
    except Exception as e:
        print(f'error in is_valid_date: {e}')
        return False
        


def time_to_date(time:float)->str:
    """
    输入纳秒时间
    返回该时刻的日期 (YYYY-MM-DD)
    """
    
    time = int(time) // 1e9 # 单位：秒
    # 1970-1-1 08:00:00
    time += 8*3600
    year = 1970
    month = 1
    while(time > year_time(year)):
        time -= year_time(year)
        year += 1
    for m in range(1,13):
        month_time = day_time * days[m]
        if(is_leap_year(year) and m == 2):
            month_time += day_time
        if(time >= month_time):
            time -= month_time
            month += 1
        else:
            break
    day = int(time // day_time + 1)
    return f"{year:04d}-{month:02d}-{day:02d}" # '2021-01-02'
    

    
        
        
def date_to_time(date:str)->int:
    """
    输入日期格式："year-month-day"
    返回纳秒时间（该日期的 00:00）
    """
    # 返回纳秒时间
    year,month,day = map(int,date.split('-'))
    res = -8*3600
    for y in range(1970,year):
        res += year_time(y)
    res += in_year_time(year,month,day)
    return int(res * 1e9)
    






#=======  验证 0 对应 1970-1-1 08:00:00  ===========
# s=1728748800 +8*3600
# for y in range(1970,2024):
#     s -= year_time(y)
# s -= in_year_time(2024,10,13)
# print(s)


