import streamlit as st
import json
import os
from datetime import date, timedelta
import calendar 

# --- 초기 설정 및 데이터 관리 함수 ---
DATA_FILE = "calendar_data.json"
COLOR_PALETTE = [
    "#3498db", "#f1c40f", "#e74c3c", "#9b59b6", "#2ecc71",
    "#1abc9c", "#e67e22", "#34495e", "#7f8c8d", "#d35400"
]

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f: return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError): return {}
    return {}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_user_colors(users):
    return {user: COLOR_PALETTE[i % len(COLOR_PALETTE)] for i, user in enumerate(users)}

# --- Streamlit UI 구성 ---
st.set_page_config(layout="wide", page_title="여름 휴가 공유 캘린더")

# 달력 전용 CSS
st.markdown("""
    <style>
        .calendar-table { border: 1px solid #dfe6e9; border-collapse: collapse; text-align: center; width: 100%; color: #000000; }
        .calendar-table th { background-color: #3498db; color: white !important; padding: 12px; font-weight: bold; }
        .calendar-table td { height: 100px; vertical-align: top; padding: 5px; border: 1px solid #dfe6e9; }
        .day-number { font-weight: bold; font-size: 1.1em; color: #2c3e50; text-align: left; padding-left: 5px; }
        .weekend { background-color: #FFEBEE !important; }
        .other-month { background-color: #f8f9fa; }
        .current-month { background-color: #ffffff; }
        .user-tag { color: white !important; border-radius: 5px; padding: 2px 6px; font-size: 0.8em; margin: 2px 0; display: block; text-align: left; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    </style>
""", unsafe_allow_html=True)

st.title("🗓️ 여름 휴가 공유 캘린더")

# --- 사이드바 (휴가 신청 영역) ---
# 이 부분은 완벽하게 작동하므로 수정하지 않았습니다.
with st.sidebar:
    st.header("🏖️ 휴가 신청하기")
    name = st.text_input("이름을 입력하세요", key="name_input")
    available_days = 5
    
    today = date.today()
    current_year = today.year
    
    start_date = st.date_input(
        "휴가 시작일", value=None,
        min_value=date(current_year, 7, 1), max_value=date(current_year, 8, 31),
        key="start_date"
    )
    
    end_date = st.date_input(
        "휴가 종료일", value=None,
        min_value=date(current_year, 7, 1), max_value=date(current_year, 8, 31),
        key="end_date"
    )

    vacation_days = []
    error_message = ""

    if start_date and end_date:
        if end_date < start_date:
            error_message = "오류: 종료일은 시작일보다 빠를 수 없습니다."
        elif start_date.weekday() >= 5 or end_date.weekday() >= 5:
            error_message = "오류: 시작일과 종료일은 주말이 될 수 없습니다."
        else:
            current_date = start_date
            while current_date <= end_date:
                if current_date.weekday() < 5:
                    vacation_days.append(current_date)
                current_date += timedelta(days=1)
            
            if len(vacation_days) > available_days:
                error_message = f"오류: 휴가일은 주말 제외 {available_days}일을 초과할 수 없습니다."

    st.write("---")
    st.write("**선택된 휴가일 (주말 제외)**")
    
    if error_message:
        st.error(error_message)
        vacation_days = []
    
    if vacation_days:
        locale_weekdays = ["월", "화", "수", "목", "금", "토", "일"]
        for d in vacation_days:
            st.write(f"• {d.strftime('%Y년 %m월 %d일')} ({locale_weekdays[d.weekday()]})")
        st.info(f"✅ 총 **{len(vacation_days)}**일의 휴가가 선택되었습니다.")
    else:
        st.write("시작일과 종료일을 선택해주세요.")

    st.write("---")

    if st.button("제출하기", type="primary", use_container_width=True):
        if not name.strip():
            st.error("이름을 입력해주세요.")
        elif not vacation_days:
            st.error("유효한 휴가 기간을 선택해주세요.")
        elif error_message:
            st.error("오류를 수정한 후 다시 제출해주세요.")
        else:
            data = load_data()
            data[name] = [d.strftime("%Y-%m-%d") for d in vacation_days]
            save_data(data)
            st.success("휴가 신청이 완료되었습니다!")
            st.balloons()
            st.rerun()

# --- 메인 화면 (전체 캘린더) ---
data = load_data()
date_map = {}
for person, dates in data.items():
    for d_str in dates:
        date_map.setdefault(d_str, []).append(person)

all_users = sorted(list(data.keys()))
user_colors = get_user_colors(all_users)

st.header("📅 7월 & 8월 휴가 현황")
current_year = date.today().year
col1, col2 = st.columns(2)

for i, month in enumerate([7, 8]):
    target_col = col1 if i == 0 else col2
    with target_col:
        st.subheader(f"{month}월")
        
        py_cal = calendar.Calendar(firstweekday=6) 
        
        month_days = py_cal.itermonthdates(current_year, month)
        
        cal_html = '<table class="calendar-table"><tr>'
        for weekday in ["일", "월", "화", "수", "목", "금", "토"]: cal_html += f"<th>{weekday}</th>"
        cal_html += "</tr><tr>"
        
        day_count = 0
        for day in month_days:
            d_str = day.strftime("%Y-%m-%d")
            names = date_map.get(d_str, [])
            cell_class = "other-month" if day.month != month else ("weekend" if day.weekday() in [5, 6] else "current-month")
            cal_html += f'<td class="{cell_class}">'
            if day.month == month:
                cal_html += f'<div class="day-number">{day.day}</div>'
                for name in names:
                    color = user_colors.get(name, '#bdc3c7')
                    cal_html += f'<div class="user-tag" style="background-color:{color};">{name}</div>'
            cal_html += "</td>"
            day_count += 1
            if day_count % 7 == 0: cal_html += "</tr><tr>"
        
        cal_html += "</tr></table>"
        st.markdown(cal_html, unsafe_allow_html=True)
