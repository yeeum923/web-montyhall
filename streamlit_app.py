import random
import streamlit as st
import pandas as pd
try:
    import matplotlib.pyplot as plt
    HAS_MPL = True
except Exception:
    HAS_MPL = False


def plot_bar_with_fallback(labels, rates, title=None, ylim=(0, 100)):
    if HAS_MPL:
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.bar(labels, rates, color=['#6ea8fe', '#ffd166'])
        ax.set_ylim(ylim)
        ax.set_ylabel('승률 (%)')
        if title:
            ax.set_title(title)
        st.pyplot(fig)
    else:
        df = pd.DataFrame({'rate': rates}, index=labels)
        st.bar_chart(df['rate'])


def plot_line_with_fallback(x, y1, y2):
    if HAS_MPL:
        fig, ax = plt.subplots(figsize=(8, 3))
        ax.plot(x, y1, label='유지 승률')
        ax.plot(x, y2, label='변경 승률')
        ax.axhline(33.333, color='gray', linestyle='--', label='유지 이론(33.3%)')
        ax.axhline(66.666, color='gray', linestyle=':', label='변경 이론(66.7%)')
        ax.set_ylim(0, 100)
        ax.set_xlabel('시행 수')
        ax.set_ylabel('승률 (%)')
        ax.legend()
        st.pyplot(fig)
    else:
        df = pd.DataFrame({'유지': y1, '변경': y2}, index=x)
        st.line_chart(df)

# 페이지 설정
st.set_page_config(page_title="몬티홀 실험실 🎉", layout="wide")

# 스타일
st.markdown(
    """
    <style>
        .stApp { background: #0b1220; color: #ffffff; }
        .main { background: linear-gradient(180deg,#071026,#081726); border-radius: 12px; padding: 24px; }
        .panel { background: #071026; border-radius: 12px; padding: 18px; margin-bottom: 16px; border:1px solid #1b3558; }
        .step-title { color: #e6f0ff; font-size:18px; font-weight:700; }
        .door-card { text-align:center; padding:12px; border-radius:12px; border:2px solid #233c66; background: linear-gradient(180deg,#0b1220,#122035); color:#fff; }
        .door-emoji { font-size:36px; }
        .host { font-size:20px; color:#ffd27f; }
        .result-win { background: #143a2e; padding:12px; border-radius:8px; }
        .result-lose { background: #3a1414; padding:12px; border-radius:8px; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("""
<div class='main'>
  <h1>🔍 몬티홀 실험실</h1>
  <p>직접 실험하고 결과를 분석하며, 몬티홀 문제 속 조건부확률의 원리를 재미있게 탐구해 보세요.</p>
</div>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if 'stage_history' not in st.session_state:
    st.session_state['stage_history'] = []
if 'stats' not in st.session_state:
    st.session_state['stats'] = {'stay_attempts': 0, 'stay_success': 0, 'switch_attempts': 0, 'switch_success': 0}
if 'last_game' not in st.session_state:
    st.session_state['last_game'] = None
if 'pending' not in st.session_state:
    st.session_state['pending'] = None
if 'opinion' not in st.session_state:
    st.session_state['opinion'] = None
if 'prediction' not in st.session_state:
    st.session_state['prediction'] = {'stay': None, 'switch': None}
if 'quiz_score' not in st.session_state:
    st.session_state['quiz_score'] = None
if 'reflection' not in st.session_state:
    st.session_state['reflection'] = None

# 도우미 함수

def host_reveal(car, choice):
    doors = [1,2,3]
    return random.choice([d for d in doors if d != choice and d != car])


def play_game(choice, strategy, manual_host_open=None):
    doors = [1,2,3]
    car = random.choice(doors)
    opened = manual_host_open if manual_host_open is not None else host_reveal(car, choice)
    final = choice if strategy == '유지' else [d for d in doors if d != choice and d != opened][0]
    win = final == car
    return {'choice': choice, 'opened': opened, 'final': final, 'car': car, 'win': win}


def update_stats(result, strategy):
    st.session_state['stage_history'].append({'strategy': strategy, **result})
    if strategy == '유지':
        st.session_state['stats']['stay_attempts'] += 1
        if result['win']:
            st.session_state['stats']['stay_success'] += 1
    else:
        st.session_state['stats']['switch_attempts'] += 1
        if result['win']:
            st.session_state['stats']['switch_success'] += 1


def stats_table():
    s = st.session_state['stats']
    rows = [
        {'전략': '유지', '시행횟수': s['stay_attempts'], '성공횟수': s['stay_success'], '승률(%)': round((s['stay_success'] / s['stay_attempts'] * 100) if s['stay_attempts'] else 0,1)},
        {'전략': '변경', '시행횟수': s['switch_attempts'], '성공횟수': s['switch_success'], '승률(%)': round((s['switch_success'] / s['switch_attempts'] * 100) if s['switch_attempts'] else 0,1)},
    ]
    return pd.DataFrame(rows)


def simulate(n):
    # return cumulative results after each block for plotting
    history = []
    for i in range(n):
        c = random.choice([1,2,3])
        r1 = play_game(c, '유지')
        update_stats(r1, '유지')
        # record snapshot every 10% or at end
        if (i+1) % max(1, n//10) == 0 or i==n-1:
            df = stats_table()
            history.append({'trials': i+1, 'stay_rate': df.loc[0,'승률(%)'], 'switch_rate': df.loc[1,'승률(%)']})
    for i in range(n):
        c = random.choice([1,2,3])
        r2 = play_game(c, '변경')
        update_stats(r2, '변경')
        if (i+1) % max(1, n//10) == 0 or i==n-1:
            df = stats_table()
            history.append({'trials': n + i+1, 'stay_rate': df.loc[0,'승률(%)'], 'switch_rate': df.loc[1,'승률(%)']})
    return history

# 단계 선택
step = st.selectbox('학습 단계 선택', [
    '1. 생각해보기 💭',
    '2. 직접 체험하기 🎮',
    '3. 결과 분석 📊',
    '4. 대규모 자동 시뮬레이션 🚀',
    '5. 조건부확률 이해 🔍',
    '6. 학습 정리 📝',
])

# 1단계: 생각해보기
if step == '1. 생각해보기 💭':
    st.markdown("""
    <div class='panel'>
      <div class='step-title'>1단계: 생각해보기 💡</div>
      <p>사회자가 문 하나를 열어준 후, 어떤 전략이 더 유리하다고 생각하나요? 🤔</p>
    </div>
    """, unsafe_allow_html=True)
    opinion = st.radio('당신의 직관을 선택하세요', ['유지가 유리하다 👍', '변경이 유리하다 🔁', '둘 다 같다 😐'])
    reason = st.text_area('왜 그렇게 생각하나요? (간단히 서술)', value='')
    if st.button('생각 저장 💾'):
        st.session_state['opinion'] = opinion
        st.session_state['reason'] = reason
        st.success('생각이 저장되었습니다.')
    if st.session_state.get('opinion'):
        st.info(f"저장된 생각: {st.session_state.get('opinion')} — 이유: {st.session_state.get('reason','(없음)')}")

# 2단계: 직접 체험하기 (2단계 흐름 적용)
elif step == '2. 직접 체험하기 🎮':
    st.markdown("""
    <div class='panel'>
      <div class='step-title'>2단계: 직접 체험하기 🎮</div>
      <p>문을 선택하고, 사회자가 염소 문을 공개하면 유지 또는 변경을 선택하세요.</p>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(3)
    for i, col in enumerate(cols, start=1):
        with col:
            st.markdown(f"<div class='door-card'><div class='door-emoji'>🚪</div><h3>문 {i}</h3></div>", unsafe_allow_html=True)
            if st.button(f'문 {i} 선택 🚪', key=f'select_{i}'):
                # create a pending game: record player's initial choice and host's reveal
                car = random.choice([1,2,3])
                opened = host_reveal(car, i)
                st.session_state['pending'] = {'choice': i, 'car': car, 'opened': opened}

    if st.session_state.get('pending'):
        p = st.session_state['pending']
        st.markdown(f"<div class='panel'><div class='host'>🎤 사회자: '문 {p['opened']}을 열어보겠습니다.'</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='panel'>🐐 염소가 나왔습니다! (문 {p['opened']})</div>", unsafe_allow_html=True)
        st.markdown('이제 전략을 선택하세요: 🎯')
        col1, col2 = st.columns(2)
        with col1:
            if st.button('유지 👍', key='stay_btn'):
                res = play_game(p['choice'], '유지', manual_host_open=p['opened'])
                update_stats(res, '유지')
                st.session_state['last_game'] = {'strategy': '유지', **res}
                st.session_state['pending'] = None
        with col2:
            if st.button('변경 🔁', key='switch_btn'):
                res = play_game(p['choice'], '변경', manual_host_open=p['opened'])
                update_stats(res, '변경')
                st.session_state['last_game'] = {'strategy': '변경', **res}
                st.session_state['pending'] = None

    if st.session_state.get('last_game'):
        g = st.session_state['last_game']
        if g['win']:
            st.markdown("<div class='result-win'>🎉 축하합니다! 자동차에 당첨되었습니다! 🚗</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='result-lose'>🐐 아쉽네요. 염소였습니다.</div>", unsafe_allow_html=True)
        st.markdown(f"- 처음 선택한 문: 문 {g['choice']}")
        st.markdown(f"- 공개된 문: 문 {g['opened']}")
        st.markdown(f"- 최종 선택한 문: 문 {g['final']}")
        st.markdown(f"- 자동차 위치: 문 {g['car']}")

    if st.button('통계 초기화'):
        st.session_state['stage_history'] = []
        st.session_state['stats'] = {'stay_attempts': 0, 'stay_success': 0, 'switch_attempts': 0, 'switch_success': 0}
        st.session_state['last_game'] = None
        st.session_state['pending'] = None
        st.success('통계가 초기화되었습니다.')

# 3단계: 결과 분석
elif step == '3. 결과 분석 📊':
    st.markdown("""
    <div class='panel'>
      <div class='step-title'>3단계: 결과 분석 📊</div>
      <p>누적된 실험 결과를 표로 확인하고, 어떤 전략이 더 잘 작동했는지 알아봐요.</p>
    </div>
    """, unsafe_allow_html=True)
    df = stats_table()
    st.table(df)
    st.markdown(f"총 실험 횟수: {len(st.session_state['stage_history'])} 회")

# 4단계: 대규모 자동 시뮬레이션
elif step == '4. 대규모 자동 시뮬레이션 🚀':
    st.markdown("""
    <div class='panel'>
      <div class='step-title'>4단계: 대규모 자동 시뮬레이션 🚀</div>
      <p>박진감 넘치는 실험을 반복 실행해 확률이 어떻게 수렴하는지 확인해 봅시다.</p>
    </div>
    """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    hist = None
    with col1:
        if st.button('100회 🔢'):
            hist = simulate(100)
            st.success('100회 자동 실험 완료 🎉')
    with col2:
        if st.button('1,000회 🌟'):
            hist = simulate(1000)
            st.success('1,000회 자동 실험 완료 🎉')
    with col3:
        if st.button('10,000회 🚀'):
            hist = simulate(10000)
            st.success('10,000회 자동 실험 완료 🎉')

    df = stats_table()
    st.table(df)

    if hist:
        hdf = pd.DataFrame(hist)
        plot_line_with_fallback(hdf['trials'], hdf['stay_rate'], hdf['switch_rate'])

# 5단계: 조건부확률 이해 (미니 수업)
elif step == '5. 조건부확률 이해 🔍':
    st.markdown("""
    <div class='panel'>
      <div class='step-title'>5단계. 왜 선택을 바꾸는 것이 더 유리할까? 🔍</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
## 먼저 생각해보기
많은 사람들은 몬티홀 문제를 처음 보면 이렇게 생각합니다.

"문이 세 개였는데 하나가 열렸으니 이제 문이 두 개 남았다. 그렇다면 확률은 1/2 대 1/2 아닌가?"

정말 그럴까요?

실제로는 그렇지 않습니다.

---

## 처음 선택이 맞을 확률은 얼마일까?
처음에 자동차가 있는 문을 고를 확률은

1/3

입니다.

반대로 처음 선택이 틀릴 확률은

2/3

입니다.

즉,

- 처음부터 자동차를 고를 확률 : 1/3
- 처음부터 염소를 고를 확률 : 2/3

입니다.

---

## 사회자는 아무 문이나 여는 것이 아니다
여기서 중요한 사실이 있습니다.

사회자는 자동차가 어디에 있는지 알고 있습니다.

따라서 사회자는

- 자동차가 있는 문은 열지 않고
- 염소가 있는 문만 골라서 공개합니다.

즉, 사회자의 행동에는 중요한 정보가 담겨 있습니다.

---

## 경우를 하나씩 살펴보자
처음에 항상 문 1을 선택했다고 가정해 봅시다.
""", unsafe_allow_html=False)
    table = pd.DataFrame([
        {'자동차 위치': '문 1', '유지 전략': '성공', '변경 전략': '실패'},
        {'자동차 위치': '문 2', '유지 전략': '실패', '변경 전략': '성공'},
        {'자동차 위치': '문 3', '유지 전략': '실패', '변경 전략': '성공'},
    ])
    st.table(table)
    st.markdown("""
결과를 보면

- 유지 전략 성공 : 1번
- 변경 전략 성공 : 2번

입니다.

따라서

유지 전략의 성공 확률은 1/3,

변경 전략의 성공 확률은 2/3

입니다.

---

## 왜 확률이 1/2이 아닐까?
사회자가 문 하나를 열어도 처음 선택의 확률은 변하지 않습니다.

처음 선택한 문이 자동차일 확률은 여전히 1/3입니다.

반대로 처음 선택이 틀렸을 확률은 여전히 2/3입니다.

사회자는 염소 문만 열기 때문에, 처음 선택이 틀렸던 경우의 확률 2/3이 남은 문 하나에 그대로 모이게 됩니다.

그래서

- 처음 선택한 문 : 1/3
- 남은 다른 문 : 2/3

이 됩니다.

---

## 문이 100개라면?
문이 100개 있다고 생각해 봅시다.

- 자동차가 있는 문 1개
- 염소가 있는 문 99개

당신이 문 하나를 선택했습니다.

처음 선택이 맞을 확률은

1/100

뿐입니다.

이후 사회자가 염소가 있는 문 98개를 열어 주고,

처음 선택한 문과 다른 문 1개만 남겨 둡니다.

이때도 처음 선택이 맞을 확률은 여전히 1/100입니다.

반대로 처음 선택이 틀렸을 확률은 99/100이므로, 남은 다른 문에는 99/100의 확률이 모이게 됩니다.

따라서 대부분의 사람들은 이 경우에는 선택을 바꾸는 것이 유리하다는 것을 쉽게 받아들입니다.

사실 문이 3개인 원래 몬티홀 문제도 같은 원리입니다.

---

## 실험 결과와 비교해 보자
여러분의 실험 결과는 어땠나요?

실험 횟수가 많아질수록

- 유지 전략은 약 33%
- 변경 전략은 약 67%

에 가까워집니다.

즉, 실험 결과가 이론적으로 계산한 확률과 점점 비슷해지는 것을 확인할 수 있습니다.

---

## 핵심 정리

1. 처음 선택이 맞을 확률은 1/3이다.
2. 처음 선택이 틀릴 확률은 2/3이다.
3. 사회자는 자동차가 있는 문을 열지 않고 염소 문만 공개한다.
4. 따라서 남은 문에는 원래의 2/3 확률이 모인다.
5. 그래서 선택을 변경하는 전략의 성공 확률은 2/3이다.
""", unsafe_allow_html=False)
    df = stats_table()
    st.table(df)
    st.markdown('- 이론값: 유지 = 33.3%, 변경 = 66.7%')

# 6단계: 학습 정리 (퀴즈 + 성찰)
elif step == '6. 학습 정리 📝':
    st.markdown("""
    <div class='panel'>
      <div class='step-title'>6단계: 학습 정리 📝</div>
      <p>퀴즈로 학습 내용을 점검하고, 간단한 성찰을 작성하세요.</p>
    </div>
    """, unsafe_allow_html=True)
    q1 = st.radio('Q1. 선택을 변경하는 전략의 성공 확률은? 🎯', ['1/3','1/2','2/3','모르겠다'])
    q2 = st.radio('Q2. 사회자가 공개하는 문은? 🧐', ['플레이어가 선택한 문','자동차가 있는 문','염소가 있는 문','무작위 문'])
    q3 = st.radio('Q3. 처음 선택이 틀릴 확률은? 🤔', ['1/3','1/2','2/3','모르겠다'])
    if st.button('정답 확인 ✅'):
        score = 0
        explanations = []
        if q1 == '2/3':
            score += 1
        else:
            explanations.append('Q1: 처음 선택이 맞을 확률은 1/3, 틀릴 확률은 2/3입니다. 사회자는 염소가 있는 문만 공개하므로, 처음 선택이 틀렸던 경우(2/3)에는 선택을 변경하면 자동차를 얻게 됩니다.')
        if q2 == '염소가 있는 문':
            score += 1
        else:
            explanations.append('Q2: 사회자는 자동차의 위치를 알고 있으며, 자동차가 있는 문은 열지 않습니다. 따라서 항상 염소가 있는 문만 공개합니다.')
        if q3 == '2/3':
            score += 1
        else:
            explanations.append('Q3: 자동차는 3개의 문 중 1개 뒤에만 있으므로, 처음 선택이 맞을 확률은 1/3입니다. 따라서 처음 선택이 틀릴 확률은 2/3입니다.')
        st.session_state['quiz_score'] = score
        st.success(f'퀴즈 점수: {score} / 3')
        if explanations:
            for e in explanations:
                st.info(e)
        if st.button('다시 풀기'):
            st.session_state['quiz_score'] = None
            st.experimental_rerun()

    st.markdown('성찰: 오늘 새롭게 알게 된 점 또는 가장 놀라웠던 점을 적어보세요 ✍️')
    refl = st.text_area('성찰 작성', value='')
    if st.button('성찰 저장 💾'):
        st.session_state['reflection'] = refl
        st.success('성찰이 저장되었습니다.')
    if st.session_state.get('reflection'):
        st.info(f"저장된 성찰: {st.session_state.get('reflection')}")

# 공통: 현재 통계 표시 (화면 우측)
st.sidebar.header('📊 현재 누적 통계')
side_df = stats_table()
st.sidebar.table(side_df)
st.sidebar.markdown(f"총 실험: {len(st.session_state['stage_history'])} 회")
st.sidebar.markdown('이론값: 유지 33.3% / 변경 66.7%')

# 저장 버튼
if st.sidebar.button('결과 저장(CSV) 💾'):
    hist = pd.DataFrame(st.session_state['stage_history'])
    hist.to_csv('monty_results.csv', index=False)
    st.sidebar.success('monty_results.csv로 저장되었습니다.')
