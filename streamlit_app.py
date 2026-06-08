import random
import streamlit as st
import pandas as pd
try:
    import matplotlib.pyplot as plt
    HAS_MPL = True
except Exception:
    HAS_MPL = False


def plot_bar_with_fallback(labels, rates, title=None, ylim=(0, 100)):
    """그래프를 다크모드 테마로 렌더링"""
    if HAS_MPL:
        fig, ax = plt.subplots(figsize=(6, 3), facecolor='#0b1220')
        ax.set_facecolor('#071026')
        ax.bar(labels, rates, color=['#6ea8fe', '#ffd166'])
        ax.set_ylim(ylim)
        ax.set_ylabel('승률 (%)', color='#e6f0ff', fontsize=10)
        ax.tick_params(colors='#e6f0ff')
        ax.spines['bottom'].set_color('#1b3558')
        ax.spines['left'].set_color('#1b3558')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        if title:
            ax.set_title(title, color='#e6f0ff', fontsize=12, fontweight='bold')
        st.pyplot(fig, use_container_width=True)
    else:
        df = pd.DataFrame({'rate': rates}, index=labels)
        st.bar_chart(df['rate'])


def plot_line_with_fallback(x, y1, y2):
    """누적 승률 그래프를 다크모드 테마로 렌더링"""
    if HAS_MPL:
        fig, ax = plt.subplots(figsize=(10, 4), facecolor='#0b1220')
        ax.set_facecolor('#071026')
        ax.plot(x, y1, label='유지 전략', linewidth=2.5, color='#6ea8fe', marker='o', markersize=3)
        ax.plot(x, y2, label='변경 전략', linewidth=2.5, color='#ffd166', marker='s', markersize=3)
        ax.axhline(33.333, color='#4b5c7c', linestyle='--', linewidth=1.5, label='이론값: 유지(33.3%)', alpha=0.7)
        ax.axhline(66.666, color='#8b7c54', linestyle=':', linewidth=1.5, label='이론값: 변경(66.7%)', alpha=0.7)
        ax.set_ylim(0, 100)
        ax.set_xlabel('누적 시행 수', color='#e6f0ff', fontsize=10)
        ax.set_ylabel('승률 (%)', color='#e6f0ff', fontsize=10)
        ax.tick_params(colors='#e6f0ff')
        ax.spines['bottom'].set_color('#1b3558')
        ax.spines['left'].set_color('#1b3558')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.legend(facecolor='#071026', edgecolor='#1b3558', labelcolor='#e6f0ff', loc='best')
        ax.grid(axis='y', alpha=0.2, color='#1b3558')
        st.pyplot(fig, use_container_width=True)
    else:
        df = pd.DataFrame({'유지': y1, '변경': y2}, index=x)
        st.line_chart(df)

# 페이지 설정
st.set_page_config(page_title="몬티홀 실험실 🎉", layout="wide")

# 전역 스타일 및 다크모드 테마
st.markdown(
    """
    <style>
        /* 전체 앱 배경 */
        .stApp { background: #0b1220; color: #ffffff; }
        .main { background: linear-gradient(180deg,#071026,#081726); border-radius: 12px; padding: 24px; }
        
        /* 패널 스타일 */
        .panel { 
            background: #071026; 
            border-radius: 12px; 
            padding: 18px; 
            margin-bottom: 16px; 
            border: 1px solid #1b3558;
        }
        .panel-success {
            background: #0d2818;
            border: 1px solid #2b8a3e;
            border-radius: 12px;
            padding: 18px;
            margin-bottom: 16px;
        }
        .panel-error {
            background: #2d0a0a;
            border: 1px solid #8b3a3a;
            border-radius: 12px;
            padding: 18px;
            margin-bottom: 16px;
        }
        
        /* 제목 및 텍스트 */
        .step-title { color: #e6f0ff; font-size: 18px; font-weight: 700; }
        .host-message { font-size: 18px; color: #ffd27f; font-weight: 600; }
        
        /* 문 카드 스타일 */
        .door-card { 
            text-align: center; 
            padding: 20px; 
            border-radius: 12px; 
            border: 2px solid #233c66; 
            background: linear-gradient(180deg,#0b1220,#122035); 
            color: #fff;
            transition: all 0.3s;
        }
        .door-card-selected {
            border: 3px solid #ffd27f;
            background: linear-gradient(180deg,#2d2a0a,#3d3510);
            box-shadow: 0 0 20px rgba(255, 210, 127, 0.3);
        }
        .door-card-opened {
            border: 2px solid #4b5c7c;
            background: #051015;
            opacity: 0.6;
        }
        .door-emoji { font-size: 48px; margin: 10px 0; }
        
        /* 결과 표시 */
        .result-win { 
            background: #0d2818; 
            padding: 16px; 
            border-radius: 8px;
            border-left: 4px solid #2b8a3e;
            color: #7cfc00;
            font-weight: 600;
            font-size: 16px;
        }
        .result-lose { 
            background: #2d0a0a; 
            padding: 16px; 
            border-radius: 8px;
            border-left: 4px solid #8b3a3a;
            color: #ff6b6b;
            font-weight: 600;
            font-size: 16px;
        }
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

# 세션 상태 초기화 (기존 로직 유지)
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
if 'current_step' not in st.session_state:
    st.session_state['current_step'] = '1. 생각해보기 💭'
if 'door_state' not in st.session_state:
    st.session_state['door_state'] = None  # 게임쇼 단계 추적

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

# ============= 사이드바: 단계 선택 (활성 표시 포함) =============
st.sidebar.markdown('### 📚 학습 단계 선택')
steps = [
    '1. 생각해보기 💭',
    '2. 직접 체험하기 🎮',
    '3. 결과 분석 📊',
    '4. 대규모 자동 시뮬레이션 🚀',
    '5. 조건부확률 이해 🔍',
    '6. 학습 정리 📝',
]
for s in steps:
    # 현재 활성 단계 표시
    if s == st.session_state['current_step']:
        if st.sidebar.button(f"✨ {s}", use_container_width=True, key=f"btn_{s}"):
            st.session_state['current_step'] = s
            st.rerun()
    else:
        if st.sidebar.button(s, use_container_width=True, key=f"btn_{s}"):
            st.session_state['current_step'] = s
            st.rerun()

st.sidebar.markdown('---')

step = st.session_state['current_step']


# ============= 1단계: 생각해보기 =============
if step == '1. 생각해보기 💭':
    st.markdown("""
    <div class='panel'>
      <div class='step-title'>1단계: 생각해보기 💡</div>
      <p>사회자가 문 하나를 열어준 후, 어떤 전략이 더 유리하다고 생각하나요? 🤔</p>
    </div>
    """, unsafe_allow_html=True)
    
    opinion = st.radio('당신의 직관을 선택하세요', ['유지가 유리하다 👍', '변경이 유리하다 🔁', '둘 다 같다 😐'])
    reason = st.text_area('왜 그렇게 생각하나요? (간단히 서술)', value='')
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button('생각 저장 💾', use_container_width=True):
            st.session_state['opinion'] = opinion
            st.session_state['reason'] = reason
            st.success('생각이 저장되었습니다.')
    
    with col2:
        if st.button('다음 단계로 → 2단계', use_container_width=True):
            st.session_state['current_step'] = '2. 직접 체험하기 🎮'
            st.rerun()
    
    if st.session_state.get('opinion'):
        st.markdown(f"""
        <div class='panel-success'>
            <strong>💭 저장된 생각:</strong><br>
            {st.session_state.get('opinion')}<br>
            <strong>이유:</strong> {st.session_state.get('reason', '(없음)')}
        </div>
        """, unsafe_allow_html=True)

# ============= 2단계: 직접 체험하기 (게임쇼 흐름) =============
elif step == '2. 직접 체험하기 🎮':
    st.markdown("""
    <div class='panel'>
      <div class='step-title'>2단계: 직접 체험하기 🎮</div>
      <p>문을 선택하고, 사회자가 염소 문을 공개한 뒤 전략을 선택해보세요!</p>
    </div>
    """, unsafe_allow_html=True)

    # =========== 게임 상태 머신 ===========
    if st.session_state['pending'] is None:
        # 상태: 문 선택 전
        st.markdown("### 🚪 어느 문을 선택하시겠습니까?")
        cols = st.columns(3)
        for i, col in enumerate(cols, start=1):
            with col:
                st.markdown(f"<div class='door-card'><div class='door-emoji'>🚪</div><h4>문 {i}</h4></div>", unsafe_allow_html=True)
                if st.button(f'선택', use_container_width=True, key=f'select_{i}'):
                    car = random.choice([1, 2, 3])
                    opened = host_reveal(car, i)
                    st.session_state['pending'] = {'choice': i, 'car': car, 'opened': opened, 'stage': 'revealed'}
                    st.rerun()
    else:
        p = st.session_state['pending']
        
        # 상태: 문 선택 후, 사회자가 개방 전/후
        if p['stage'] == 'revealed':
            # 선택한 문 강조 표시
            st.markdown(f"### 🟡 당신이 선택한 문: **문 {p['choice']}**")
            
            # 사회자 멘트
            st.markdown(f"""
            <div class='panel-error'>
                <div class='host-message'>🎤 사회자: "흠... 그럼 저는 문 {p['opened']}을 열어보겠습니다."</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"### 🐐 문 {p['opened']}에서 염소가 나왔습니다!")
            
            # 남은 두 개 문 시각화
            remaining = [d for d in [1, 2, 3] if d != p['opened']]
            cols = st.columns(2)
            with cols[0]:
                door_num = remaining[0]
                if door_num == p['choice']:
                    st.markdown(f"<div class='door-card door-card-selected'><div class='door-emoji'>🚪</div><h4>문 {door_num}</h4><small>선택함</small></div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='door-card'><div class='door-emoji'>🚪</div><h4>문 {door_num}</h4></div>", unsafe_allow_html=True)
            
            with cols[1]:
                door_num = remaining[1]
                if door_num == p['choice']:
                    st.markdown(f"<div class='door-card door-card-selected'><div class='door-emoji'>🚪</div><h4>문 {door_num}</h4><small>선택함</small></div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='door-card'><div class='door-emoji'>🚪</div><h4>문 {door_num}</h4></div>", unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("### 🎯 이제 선택하세요: 유지할까요, 변경할까요?")
            st.markdown("*\"직관을 믿으시겠습니까? 아니면 수학을 믿으시겠습니까?\"*")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button('👍 선택 유지', use_container_width=True, key='stay_btn'):
                    res = play_game(p['choice'], '유지', manual_host_open=p['opened'])
                    update_stats(res, '유지')
                    st.session_state['last_game'] = {'strategy': '유지', **res}
                    st.session_state['pending'] = None
                    st.rerun()
            
            with col2:
                if st.button('🔁 선택 변경', use_container_width=True, key='switch_btn'):
                    res = play_game(p['choice'], '변경', manual_host_open=p['opened'])
                    update_stats(res, '변경')
                    st.session_state['last_game'] = {'strategy': '변경', **res}
                    st.session_state['pending'] = None
                    st.rerun()

    # 게임 결과 표시
    if st.session_state.get('last_game'):
        g = st.session_state['last_game']
        st.markdown("---")
        st.markdown("### 🎬 결과 발표!")
        
        if g['win']:
            st.markdown("<div class='result-win'>🎉 축하합니다! 자동차에 당첨되었습니다! 🚗</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='result-lose'>🐐 아쉽네요. 염소였습니다...</div>", unsafe_allow_html=True)
        
        # 디테일 정보
        result_cols = st.columns(4)
        with result_cols[0]:
            st.metric("처음 선택", f"문 {g['choice']}")
        with result_cols[1]:
            st.metric("사회자 개방", f"문 {g['opened']}")
        with result_cols[2]:
            st.metric("최종 선택", f"문 {g['final']}")
        with result_cols[3]:
            st.metric("정답", f"문 {g['car']}")
        
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button('🔄 다시 플레이', use_container_width=True):
                st.session_state['last_game'] = None
                st.session_state['pending'] = None
                st.rerun()
        
        with col2:
            if st.button('다음 단계로 → 3단계', use_container_width=True):
                st.session_state['current_step'] = '3. 결과 분석 📊'
                st.rerun()
    
    st.markdown("---")
    if st.button('🔄 모든 데이터 초기화'):
        st.session_state['stage_history'] = []
        st.session_state['stats'] = {'stay_attempts': 0, 'stay_success': 0, 'switch_attempts': 0, 'switch_success': 0}
        st.session_state['last_game'] = None
        st.session_state['pending'] = None
        st.success('모든 데이터가 초기화되었습니다.')

# ============= 3단계: 결과 분석 =============
elif step == '3. 결과 분석 📊':
    st.markdown("""
    <div class='panel'>
      <div class='step-title'>3단계: 결과 분석 📊</div>
      <p>누적된 실험 결과를 표로 확인하고, 어떤 전략이 더 잘 작동했는지 분석해봅시다.</p>
    </div>
    """, unsafe_allow_html=True)
    
    df = stats_table()
    
    # 메트릭 표시
    s = st.session_state['stats']
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("총 시행 횟수", len(st.session_state['stage_history']))
    with col2:
        stay_rate = (s['stay_success'] / s['stay_attempts'] * 100) if s['stay_attempts'] else 0
        st.metric("유지 전략 승률", f"{stay_rate:.1f}%", "이론값 33.3%")
    with col3:
        switch_rate = (s['switch_success'] / s['switch_attempts'] * 100) if s['switch_attempts'] else 0
        st.metric("변경 전략 승률", f"{switch_rate:.1f}%", "이론값 66.7%")
    
    st.markdown("### 📋 상세 통계")
    st.table(df)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button('이전 단계로 ← 2단계', use_container_width=True):
            st.session_state['current_step'] = '2. 직접 체험하기 🎮'
            st.rerun()
    with col2:
        if st.button('다음 단계로 → 4단계', use_container_width=True):
            st.session_state['current_step'] = '4. 대규모 자동 시뮬레이션 🚀'
            st.rerun()

# ============= 4단계: 대규모 자동 시뮬레이션 =============
elif step == '4. 대규모 자동 시뮬레이션 🚀':
    st.markdown("""
    <div class='panel'>
      <div class='step-title'>4단계: 대규모 자동 시뮬레이션 🚀</div>
      <p>대규모 실험을 반복 실행하여 확률이 이론값으로 수렴하는 모습을 확인하세요!</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    hist = None
    with col1:
        if st.button('⚡ 100회 시뮬레이션', use_container_width=True):
            with st.spinner('시뮬레이션 중...'):
                hist = simulate(100)
            st.success('✅ 100회 시뮬레이션 완료!')
    with col2:
        if st.button('⚡⚡ 1,000회 시뮬레이션', use_container_width=True):
            with st.spinner('시뮬레이션 중...'):
                hist = simulate(1000)
            st.success('✅ 1,000회 시뮬레이션 완료!')
    with col3:
        if st.button('⚡⚡⚡ 10,000회 시뮬레이션', use_container_width=True):
            with st.spinner('시뮬레이션 중...'):
                hist = simulate(10000)
            st.success('✅ 10,000회 시뮬레이션 완료!')
    
    st.markdown("---")
    
    # 현재 승률 메트릭
    st.markdown("### 📈 현재 누적 승률")
    df = stats_table()
    col1, col2 = st.columns(2)
    with col1:
        stay_rate = df.loc[0, '승률(%)']
        st.metric(
            "유지 전략 승률", 
            f"{stay_rate:.1f}%",
            delta=f"{stay_rate - 33.3:.1f}% vs 이론값(33.3%)"
        )
    with col2:
        switch_rate = df.loc[1, '승률(%)']
        st.metric(
            "변경 전략 승률", 
            f"{switch_rate:.1f}%",
            delta=f"{switch_rate - 66.7:.1f}% vs 이론값(66.7%)"
        )
    
    # 상세 테이블
    st.markdown("### 📊 상세 통계")
    st.table(df)
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button('이전 단계로 ← 3단계', use_container_width=True):
            st.session_state['current_step'] = '3. 결과 분석 📊'
            st.rerun()
    with col2:
        if st.button('다음 단계로 → 5단계', use_container_width=True):
            st.session_state['current_step'] = '5. 조건부확률 이해 🔍'
            st.rerun()

# ============= 5단계: 조건부확률 이해 (탭 구조) =============
elif step == '5. 조건부확률 이해 🔍':
    st.markdown("""
    <div class='panel'>
      <div class='step-title'>5단계: 조건부확률로 보는 몬티홀 문제 🔍</div>
      <p>왜 선택을 변경하면 이기는 확률이 2/3가 될까요? 수학적으로 엄밀하게 살펴봅시다.</p>
    </div>
    """, unsafe_allow_html=True)

    tabs = st.tabs([
        "① 조건부확률 이란?",
        "② 몬티홀의 조건",
        "③ 확률 분석 & 경우의 수",
        "④ 직관 깨기"
    ])

    # ========== 탭 1: 조건부확률 이란? ==========
    with tabs[0]:
        st.markdown("""
#### 📖 조건부확률의 정의

어떤 사건 $B$가 이미 일어났다는 **정보를 알고 있을 때**, 그 정보를 반영하여 다시 계산한 확률을 **조건부확률**이라고 합니다.

**기호:** $P(A \\mid B)$ 
- 읽음: "$B$가 일어났을 때 $A$의 조건부확률"
- 정의: $P(A \\mid B) = \\dfrac{P(A \\cap B)}{P(B)}$ (단, $P(B) > 0$)

---

#### 🎯 각 항의 의미
- $P(A \\cap B)$: $A$와 $B$가 **동시에** 일어날 확률
- $P(B)$: 조건이 되는 사건 $B$가 일어날 확률
- $P(A \\mid B)$: 새로운 정보 $B$를 반영한 $A$의 확률

---

#### 💡 일상적 예시

상황: 어떤 학교에서 남학생 60%, 여학생 40%. 남학생 중 50%가 안경, 여학생 중 30%가 안경을 씀.

문제: 복도에서 만난 학생이 안경을 쓰고 있었습니다. 이 학생이 남학생일 확률은?

- $B$: "학생이 안경을 쓰고 있다"
- $A$: "학생이 남학생이다"
- 구하는 것: $P(A \\mid B)$ (안경을 쓰고 있다는 정보 아래에서 남학생일 확률)
        """)

    # ========== 탭 2: 몬티홀의 조건 ==========
    with tabs[1]:
        st.markdown("""
#### 🎭 몬티홀 문제에서의 핵심 조건

몬티홀 문제를 조건부확률로 정확하게 표현하려면, **어떤 조건이 주어졌는가**를 명확히 해야 합니다.

---

#### 🚪 사건의 정의

**문 1, 2, 3이 있고, 플레이어가 문 1을 선택했다고 가정:**

사건 $A_i$: 자동차가 **문 $i$ 뒤에 있다** ($i = 1, 2, 3$)
- $P(A_1) = P(A_2) = P(A_3) = \\dfrac{1}{3}$ (자동차는 무작위로 배치)

사건 $M_j$: **사회자가 문 $j$를 열어 염소를 보여준다** ($j \\neq 1$, 즉 $j = 2$ 또는 $3$)

---

#### 💥 핵심 조건: 사회자의 행동

> **"사회자는 자동차 위치를 알고 있고, 자동차가 있는 문은 절대 열지 않는다."**

이것이 몬티홀 문제의 **결정적 조건**입니다.

예를 들어:
- 자동차가 문 1에 있으면, 사회자는 문 2 또는 3 중 하나를 무작위로 선택해서 열 수 있음.
- 자동차가 문 2에 있으면, 사회자는 **반드시 문 3을 열어야 함** (문 2는 열 수 없고, 문 1도 플레이어 선택이라 열 수 없음).

---

#### 🎯 구하는 것

사회자가 문 3을 열어 염소를 보여주었을 때:
- **유지 전략의 승률:** $P(A_1 \\mid M_3)$ (사회자가 문 3을 열었을 때, 처음 선택한 문 1에 자동차가 있을 확률)
- **변경 전략의 승률:** $P(A_2 \\mid M_3)$ (사회자가 문 3을 열었을 때, 다른 문 2에 자동차가 있을 확률)
        """)

    # ========== 탭 3: 확률 분석 & 경우의 수 ==========
    with tabs[2]:
        st.markdown("""
#### 📊 경우의 수 분석

플레이어가 **문 1을 선택**했다고 가정. 자동차의 위치에 따라:

|  | 자동차 위치 | 발생 확률 | 사회자의 행동 | 유지 시 결과 | 변경 시 결과 |
|--|---------|--------|----------|----------|----------|
| **경우 1** | 문 1 | 1/3 | 문 2 또는 3 중 하나 개방 | ✅ 성공 | ❌ 실패 |
| **경우 2** | 문 2 | 1/3 | 반드시 문 3만 개방 | ❌ 실패 | ✅ 성공 |
| **경우 3** | 문 3 | 1/3 | 반드시 문 2만 개방 | ❌ 실패 | ✅ 성공 |

---

#### 🔢 베이즈 정리를 이용한 계산

사회자가 **문 3을 열었다**고 하자. $P(A_1), P(A_2), P(A_3)$는 초기 확률이고, 이제 사회자가 문 3을 열었다는 조건 $M_3$ 하에서 다시 계산합니다.

**유지 전략 ($A_1$)의 경우:**
$$P(A_1 \\mid M_3) = \\frac{P(M_3 \\mid A_1) \\cdot P(A_1)}{P(M_3)}$$

- $P(M_3 \\mid A_1)$: 자동차가 문 1에 있을 때, 사회자가 문 3을 열 확률 = $\\dfrac{1}{2}$ (문 2 또는 3 중 선택)
- $P(A_1) = \\dfrac{1}{3}$
- $P(M_3) = P(M_3 \\mid A_1)P(A_1) + P(M_3 \\mid A_2)P(A_2) + P(M_3 \\mid A_3)P(A_3)$
  - $= \\dfrac{1}{2} \\cdot \\dfrac{1}{3} + 1 \\cdot \\dfrac{1}{3} + 0 \\cdot \\dfrac{1}{3}$
  - $= \\dfrac{1}{6} + \\dfrac{1}{3} = \\dfrac{1}{2}$

따라서:
$$P(A_1 \\mid M_3) = \\frac{\\frac{1}{2} \\cdot \\frac{1}{3}}{\\frac{1}{2}} = \\frac{1}{3}$$

---

**변경 전략 ($A_2$)의 경우:**
$$P(A_2 \\mid M_3) = \\frac{P(M_3 \\mid A_2) \\cdot P(A_2)}{P(M_3)}$$

- $P(M_3 \\mid A_2) = 1$ (자동차가 문 2에 있으면, 사회자는 **반드시** 문 3을 열어야 함)
- $P(A_2) = \\dfrac{1}{3}$

따라서:
$$P(A_2 \\mid M_3) = \\frac{1 \\cdot \\frac{1}{3}}{\\frac{1}{2}} = \\frac{2}{3}$$

---

#### ✅ 결론
- **유지 전략 승률:** $\\dfrac{1}{3}$
- **변경 전략 승률:** $\\dfrac{2}{3}$

**수학적 확실함:** 선택을 변경하는 것이 2배 유리합니다.
        """)

    # ========== 탭 4: 직관 깨기 ==========
    with tabs[3]:
        st.markdown("""
#### ❌ 흔한 착각: "남은 두 문이니까 50:50이겠지?"

> **왜 이게 틀렸을까요?**

**착각의 원인:** 사회자의 행동이 **무작위가 아니라 정보를 포함한다**는 점을 간과하기 쉬움.

사회자가 "염소 문을 공개한다"는 행동 자체가 새로운 정보를 제공합니다. 이는 사회자가 자동차 위치를 알고 있다는 증거입니다.

---

#### 🎯 핵심: 정보 비대칭
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
**처음 선택할 때**
- 세 문 중 하나에 자동차
- 확률: 1/3
- 정보 수준: 동등
            """)
        with col2:
            st.markdown("""
**사회자가 문을 열었을 때**
- 사회자는 위치를 앎
- 염소 문만 염치있게 품
- 정보 수준: **비대칭**
            """)
        
        st.markdown("""
---

#### 🔬 극단적 예시: 문이 100개라면?

상황:
- 문 100개 중 자동차 1개, 염소 99개
- 플레이어가 문 1번을 선택
- 사회자가 문 2~100 중 **98개를 열어서 염소를 보여줌**
- 남은 문: 플레이어의 선택 (문 1) vs 다른 한 문 (예: 문 50)

**직관적으로 생각해보세요:**
- 처음 선택이 맞을 확률: 1/100 (거의 불가능)
- 선택을 바꿀 확률: 99/100 (거의 확실)

**수학적으로:**
- $P(\\text{처음 선택이 맞음} \\mid \\text{사회자의 선택}) = \\dfrac{1}{100}$
- $P(\\text{다른 문이 맞음} \\mid \\text{사회자의 선택}) = \\dfrac{99}{100}$

---

#### 💡 왜 1/2이 아닐까?

사회자가 단순히 "무작위로 한 문을 열어서 염소가 나왔다"면 확률이 1/2이 될 수 있습니다.

하지만 몬티홀 문제에서는:
1. 사회자가 자동차 위치를 **알고 있음**
2. 절대 자동차 문을 열지 않음 (의도적 선택)
3. 따라서 사회자의 행동이 **정보를 전달**함

이것이 조건부확률을 사용해야 하는 이유입니다.

---

#### 🧠 핵심 정리

| 개념 | 설명 |
|-----|-----|
| **조건부확률** | 새로운 정보가 주어졌을 때 확률을 다시 계산 |
| **사전 확률** | 사회자 개방 전: 각 문에 1/3 |
| **사후 확률** | 사회자 개방 후: 유지 1/3, 변경 2/3 |
| **핵심** | 사회자의 "정보를 포함한 선택"이 모든 것을 결정 |
        """)

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button('이전 단계로 ← 4단계', use_container_width=True):
            st.session_state['current_step'] = '4. 대규모 자동 시뮬레이션 🚀'
            st.rerun()
    with col2:
        if st.button('다음 단계로 → 6단계', use_container_width=True):
            st.session_state['current_step'] = '6. 학습 정리 📝'
            st.rerun()

# ============= 6단계: 학습 정리 (퀴즈) =============
elif step == '6. 학습 정리 📝':
    st.markdown("""
    <div class='panel'>
      <div class='step-title'>6단계: 학습 정리 📝</div>
      <p>퀴즈로 학습 내용을 점검하고, 간단한 성찰을 작성해보세요.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🧠 확인 퀴즈")
    q1 = st.radio('**Q1.** 선택을 변경하는 전략의 성공 확률은? 🎯', ['1/3', '1/2', '2/3', '모르겠다'])
    q2 = st.radio('**Q2.** 사회자가 공개하는 문은? 🧐', ['플레이어가 선택한 문', '자동차가 있는 문', '염소가 있는 문', '무작위 문'])
    q3 = st.radio('**Q3.** 처음 선택이 틀릴 확률은? 🤔', ['1/3', '1/2', '2/3', '모르겠다'])

    if st.button('정답 확인 및 해설 보기 ✅', use_container_width=True):
        score = 0
        explanations = []

        # Q1
        if q1 == '2/3':
            score += 1
            explanations.append(('✅ Q1 정답!', """
선택을 변경하는 전략의 성공 확률은 **2/3**입니다.

**이유:** 처음 선택이 맞을 확률은 1/3, 틀릴 확률은 2/3입니다. 
사회자가 염소가 있는 문만 공개하므로, 처음 선택이 틀렸던 경우(2/3)에 
선택을 변경하면 자동차를 얻게 됩니다.
            """))
        else:
            explanations.append(('❌ Q1 해설', """
선택을 변경하는 전략의 성공 확률은 **2/3**입니다.

**이유:** 처음 선택이 맞을 확률은 1/3, 틀릴 확률은 2/3입니다. 
사회자가 염소가 있는 문만 공개하므로, 처음 선택이 틀렸던 경우(2/3)에 
선택을 변경하면 자동차를 얻게 됩니다.
            """))

        # Q2
        if q2 == '염소가 있는 문':
            score += 1
            explanations.append(('✅ Q2 정답!', """
사회자는 **염소가 있는 문만** 공개합니다.

**이유:** 사회자는 자동차의 위치를 알고 있으며, 
자동차가 있는 문은 절대 열지 않습니다. 
따라서 항상 염소가 있는 문만 공개합니다.
            """))
        else:
            explanations.append(('❌ Q2 해설', """
사회자는 **염소가 있는 문만** 공개합니다.

**이유:** 사회자는 자동차의 위치를 알고 있으며, 
자동차가 있는 문은 절대 열지 않습니다. 
따라서 항상 염소가 있는 문만 공개합니다.
            """))

        # Q3
        if q3 == '2/3':
            score += 1
            explanations.append(('✅ Q3 정답!', """
처음 선택이 틀릴 확률은 **2/3**입니다.

**이유:** 자동차는 3개의 문 중 1개 뒤에만 있으므로, 
처음 선택이 맞을 확률은 1/3입니다. 
따라서 처음 선택이 틀릴 확률은 1 - 1/3 = 2/3입니다.
            """))
        else:
            explanations.append(('❌ Q3 해설', """
처음 선택이 틀릴 확률은 **2/3**입니다.

**이유:** 자동차는 3개의 문 중 1개 뒤에만 있으므로, 
처음 선택이 맞을 확률은 1/3입니다. 
따라서 처음 선택이 틀릴 확률은 1 - 1/3 = 2/3입니다.
            """))

        # 결과 표시
        st.markdown("---")
        if score == 3:
            st.markdown(f"""
            <div class='panel-success'>
                <h3>🎉 완벽합니다! {score} / 3 정답!</h3>
                <p>조건부확률의 개념을 정확히 이해하셨습니다. 축하합니다! 🏆</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class='panel'>
                <h3>👏 수고하셨습니다! {score} / 3 정답</h3>
                <p>아래 해설을 참고하여 개념을 더 정리해보세요.</p>
            </div>
            """, unsafe_allow_html=True)

        # 해설 표시
        for title, content in explanations:
            if title.startswith('✅'):
                st.markdown(f"""
                <div class='panel-success'>
                <strong>{title}</strong>
                <p>{content}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class='panel-error'>
                <strong>{title}</strong>
                <p>{content}</p>
                </div>
                """, unsafe_allow_html=True)

        st.session_state['quiz_score'] = score

    st.markdown("---")
    st.markdown("### ✍️ 학습 성찰")
    st.markdown("오늘 새롭게 알게 된 점 또는 가장 놀라웠던 점을 적어보세요.")
    refl = st.text_area('성찰 작성', value=st.session_state.get('reflection', ''), height=100)

    if st.button('성찰 저장 💾', use_container_width=True):
        st.session_state['reflection'] = refl
        st.success('성찰이 저장되었습니다. 📖')

    if st.session_state.get('reflection'):
        st.markdown(f"""
        <div class='panel'>
            <strong>💭 저장된 성찰:</strong>
            <p>{st.session_state.get('reflection')}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button('이전 단계로 ← 5단계', use_container_width=True):
            st.session_state['current_step'] = '5. 조건부확률 이해 🔍'
            st.rerun()
    with col2:
        if st.button('처음부터 다시 시작 🔄', use_container_width=True):
            st.session_state['current_step'] = '1. 생각해보기 💭'
            st.rerun()

# ============= 사이드바: 저장 및 기타 =============
st.sidebar.markdown('---')
st.sidebar.markdown('### 💾 데이터 관리')

if st.sidebar.button('📥 결과 저장 (CSV)', use_container_width=True):
    if len(st.session_state['stage_history']) > 0:
        hist = pd.DataFrame(st.session_state['stage_history'])
        hist.to_csv('monty_results.csv', index=False)
        st.sidebar.success('✅ monty_results.csv로 저장되었습니다!')
    else:
        st.sidebar.info('📊 저장할 데이터가 없습니다. 실험을 진행해주세요.')

if st.sidebar.button('🔄 모든 데이터 초기화', use_container_width=True):
    st.session_state['stage_history'] = []
    st.session_state['stats'] = {'stay_attempts': 0, 'stay_success': 0, 'switch_attempts': 0, 'switch_success': 0}
    st.session_state['last_game'] = None
    st.session_state['pending'] = None
    st.sidebar.warning('⚠️ 모든 데이터가 초기화되었습니다.')

st.sidebar.markdown('---')
st.sidebar.markdown('### 📈 현재 통계')
s = st.session_state['stats']
st.sidebar.metric("총 시행 횟수", len(st.session_state['stage_history']))
if s['stay_attempts'] > 0:
    st.sidebar.metric("유지 전략", f"{(s['stay_success']/s['stay_attempts']*100):.1f}%", f"({s['stay_success']}/{s['stay_attempts']})")
if s['switch_attempts'] > 0:
    st.sidebar.metric("변경 전략", f"{(s['switch_success']/s['switch_attempts']*100):.1f}%", f"({s['switch_success']}/{s['switch_attempts']})")
