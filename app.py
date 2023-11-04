import streamlit as st
import datetime
import random
import requests
import json
import pandas as pd

page = st.sidebar.selectbox('Choose your page', ['users', 'rooms', 'bookings'])

if page == 'users':
    st.title('ユーザー登録画面')

    with st.form(key='usr'):
        # user_id: int = random.randint(0,10)
        user_name: str = st.text_input('ユーザー名', max_chars=12)
        data = {
            # 'user_id': user_id,
            'user_name': user_name
        }
        submit_button = st.form_submit_button(label='ユーザー登録')

    if submit_button: 
        st.write('## 送信データ')
        # st.json(data)
        st.write('## レスポンス結果')
        url = 'http://127.0.0.1:8000/users'
        res = requests.post(
            url,
            data = json.dumps(data)
        )
        if res.status_code == 200:
            st.success('ユーザー登録完了')
        # st.write(res.status_code)
        st.json(res.json())

elif page == 'rooms':
    st.title('会議室登録画面')

    with st.form(key='room'):
        # room_id: int = random.randint(0,10)
        room_name: str = st.text_input('会議室名', max_chars=12)
        capacity: int = st.number_input('定員', step=1)
        data = {
            # 'room_id': room_id,
            'room_name': room_name,
            'capacity': capacity
        }
        submit_button = st.form_submit_button(label='会議室登録')

    if submit_button: 
        url = 'http://127.0.0.1:8000/rooms'
        res = requests.post(
            url,
            data = json.dumps(data)
        )
        if res.status_code == 200:
            st.success('会議室登録完了')
        # st.write(res.status_code)
        st.json(res.json())

elif page == 'bookings':
    st.title('会議室予約画面')

    #　ユーザー一覧の取得
    url_users = 'http://127.0.0.1:8000/users'
    res = requests.get(url_users)
    users = res.json()
   
    # ユーザー名をキー、ユーザーIDをバリューにした辞書型を作成
    users_name = {}
    for user in users:
        users_name[user['user_name']] = user['user_id']

    # 会議室一覧の取得
    url_rooms = 'http://127.0.0.1:8000/rooms'
    res = requests.get(url_rooms)
    rooms = res.json()
    
    # 会議室名をキー、会議室IDとキャパをバリューにした辞書型を作成
    rooms_name = {}
    for room in rooms:
        rooms_name[room['room_name']] = {
            'room_id': room['room_id'],
            'capacity': room['capacity']
        }
    
    st.write('### 会議室一覧')
    df_rooms = pd.DataFrame(rooms)
    df_rooms.columns = ['会議室', '定員', '会議室ID']
    st.table(df_rooms)

    url_bookings = 'http://127.0.0.1:8000/bookings'
    res = requests.get(url_bookings)
    bookings = res.json()
    df_bookings = pd.DataFrame(bookings)

    # ユーザーIDをキー、ユーザー名をバリューにした辞書型を作成
    users_id = {}
    for user in users:
        users_id[user['user_id']] = user['user_name']

     # 会議室IDをキー、会議室名とキャパをバリューにした辞書型を作成
    rooms_id = {}
    for room in rooms:
        rooms_id[room['room_id']] = {
            'room_name': room['room_name'],
            'capacity': room['capacity']
        }

    # ユーザーIDを基にユーザー名を出す関数（前に作った辞書型を利用）
    to_user_name = lambda x: users_id[x]
    # 会議室IDを基に会議室名を出す関数
    to_room_name = lambda x: rooms_id[x]['room_name']
    # x(引数)には、isoフォーマットのものが入る → isoフォーマット(文字列型)からdatime型に変換し、またstrftimeという文字列型（もう少しみやすい形）に変換する関数
    to_datetime = lambda x: datetime.datetime.fromisoformat(x).strftime('%Y/%m/%d %H:%m')

    #上の関数を特定の列に適用（map関数で各列の一つ一つの要素（行）に関数を適用）
    df_bookings['user_id'] = df_bookings['user_id'].map(to_user_name)
    df_bookings['room_id'] = df_bookings['room_id'].map(to_room_name)
    df_bookings['start_datetime'] = df_bookings['start_datetime'].map(to_datetime)
    df_bookings['end_datetime'] = df_bookings['end_datetime'].map(to_datetime)

    df_bookings = df_bookings.rename(columns={
        'user_id': '予約者名',
        'room_id': '会議室名',
        'booked_num': '予約人数',
        'start_datetime': '予約開始時間',
        'end_datetime': '予約終了時間',
        'booking_id': '予約番号'
    })

    st.write('### 予約一覧')
    st.table(df_bookings)

    with st.form(key='booking'):
        # booking_id: int = random.randint(0,10)
        user_name: str = st.selectbox('予約者名', users_name.keys())
        room_name: str = st.selectbox('会議室名', rooms_name.keys())
        booked_num: int = st.number_input('予約人数', step=1, min_value=1)
        date = st.date_input('日付を入力', min_value=datetime.date.today())
        start_time = st.time_input('開始時刻: ', value=datetime.time(hour=9, minute=0))
        end_time = st.time_input('終了時刻: ', value=datetime.time(hour=20, minute=0))
        
        submit_button = st.form_submit_button(label='予約登録')

    if submit_button: 
        user_id: int = users_name[user_name]
        room_id: int = rooms_name[room_name]['room_id']
        capacity: int = rooms_name[room_name]['capacity']
        data = {
           'user_id': user_id,
           'room_id': room_id,
           'booked_num': booked_num,
           'start_datetime': datetime.datetime(
                year = date.year,
                month = date.month,
                day = date.day,
                hour = start_time.hour,
                minute = start_time.minute
           ).isoformat(),
           'end_datetime': datetime.datetime(
                year = date.year,
                month = date.month,
                day = date.day,
                hour = end_time.hour,
                minute = end_time.minute
           ).isoformat()
        }
        # 予約人数がキャパ以上なら
        if booked_num > capacity:
            st.error(f'{room_name}の定員は、{capacity}名です。{capacity}名以下の人数を受け付けています。')
        # 開始時刻 >= 終了時刻
        elif start_time >= end_time:
            st.error('開始時刻が終了時刻を超えています。')
        elif start_time < datetime.time(hour=9, minute=0, second=0) or end_time > datetime.time(hour=20, minute=0, second=0):
            st.error('利用時間は9時から20時になります。')
        else:
            # 予約処理
            url = 'http://127.0.0.1:8000/bookings'
            res = requests.post(
                url,
                data = json.dumps(data)
            )
            if res.status_code == 200:
                st.success('予約完了')
                st.json(res.json())
            