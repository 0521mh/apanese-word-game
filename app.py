import streamlit as st
import random
import time
import json
import requests
import pandas as pd
import qrcode
from gtts import gTTS
from io import BytesIO
from datetime import datetime, timezone, timedelta

# ==========================================
# ★ 1. 새로 만든 구글 웹 앱 URL을 여기에 붙여넣으세요!
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbx-aX4jYUgWXZxKhPAbZwEzwKd_F9UmQzii2S8WgETM3s1_HhzrKW5HKxMOoxY6VwuC/exec"
# ★ 2. 교사 설정 접속 비밀번호
TEACHER_PASSWORD = "1234"
# ★ 3. 새 스트림릿 배포 후 발급받은 주소를 넣으면 QR코드가 자동 생성됩니다!
APP_PUBLIC_URL = "https://여기에-새-배포주소를-넣으세요.streamlit.app"
# ==========================================

st.set_page_config(page_title="생활일본어 1~8과 단어 게임", page_icon="🇯🇵", layout="centered")

# 1~8과 단어 암기 노트 전체 데이터 (총 147개)
VOCAB_DATA = {
    "1과": [
        ("すし", "초밥"), ("かさ", "우산"), ("て", "손"), ("まつり", "마쓰리"),
        ("にほん", "일본"), ("たこやき", "다코야키"), ("あかい", "빨갛다"), ("おいしい", "맛있다"),
        ("ねこ", "고양이"), ("いぬ", "개"), ("はな", "코"), ("ゆかた", "유카타"),
        ("かんこく", "한국")
    ],
    "2과": [
        ("さる", "원숭이"), ("ざる", "소쿠리"), ("ひゃく", "100(백)"), ("しょくじ", "식사"),
        ("びっくり", "깜짝 놀람"), ("いっぱい", "가득"), ("せんぱい", "선배"), ("でんわ", "전화"),
        ("おじいさん", "할아버지"), ("すうがく", "수학"), ("けっせき", "결석"), ("かんじ", "한자"),
        ("こうこう", "고등학교"), ("ぺらぺら", "유창하게 말하는 모양"), ("とうきょう", "도쿄"),
        ("おおさか", "오사카"), ("ほっかいどう", "홋카이도"), ("おきなわ", "오키나와")
    ],
    "3과": [
        ("おはよう", "안녕(아침 인사)"), ("おはようございます", "안녕하세요(아침 인사)"),
        ("こんにちは", "안녕, 안녕하세요(낮 인사)"), ("せんせい", "선생님"),
        ("さようなら", "잘 가요, 안녕히 가세요, 안녕히 계세요"), ("じゃあね", "안녕, 잘 가"),
        ("バイバイ", "안녕, 잘 가"), ("またね", "또 만나"), ("またあした", "내일 또 만나"),
        ("こんばんは", "안녕, 안녕하세요(저녁 인사)"), ("おやすみ", "잘 자"),
        ("おやすみなさい", "안녕히 주무세요")
    ],
    "4과": [
        ("わたし", "나, 저"), ("ぼく", "나, 저(주로 남자가 사용)"), ("はじめまして", "처음 뵙겠습니다"),
        ("ちゅうごく", "중국"), ("フランス", "프랑스"), ("ねんせい", "학년"),
        ("しょうがく", "초등학교"), ("ちゅうがく", "중학교"), ("いち", "1(일)"),
        ("に", "2(이)"), ("さん", "3(삼)"), ("よん", "4(사)"), ("ご", "5(오)"),
        ("ろく", "6(육)"), ("なな", "7(칠)"), ("はち", "8(팔)"), ("きゅう", "9(구)"),
        ("じゅう", "10(십)")
    ],
    "5과": [
        ("あに", "(나의) 형, 오빠"), ("あね", "(나의) 누나, 언니"), ("ちち", "(나의) 아버지"),
        ("いってきます", "다녀올게, 다녀오겠습니다"), ("いってらっしゃい", "잘 다녀와, 다녀오세요"),
        ("いま", "지금"), ("いもうと", "(나의) 여동생"), ("いらっしゃい", "어서 와, 어서 와요"),
        ("おかあさん", "(남의) 어머니"), ("おかえりなさい", "잘 다녀오셨어요?"), ("おかし", "과자"),
        ("おじゃまします", "실례합니다"), ("おとうさん", "(남의) 아버지"), ("おとうとさん", "(남의) 남동생"),
        ("おなまえ", "이름"), ("おにいさん", "(남의) 형, 오빠"), ("おねえさん", "(남의) 누나, 언니"),
        ("ありがとう", "고마워")
    ],
    "6과": [
        ("とんかつ", "돈가스"), ("フライドチキン", "프라이드치킨"), ("トッポギ", "떡볶이"),
        ("いただきます", "잘 먹겠습니다"), ("たべもの", "음식"), ("うた", "노래"),
        ("りょうり", "요리"), ("バスケ", "농구"), ("ダンス", "춤"),
        ("サッカー", "축구"), ("やきゅう", "야구"), ("あまり", "그다지"),
        ("すごい", "대단하다"), ("スポーツ", "스포츠"), ("クレープ", "크레이프"),
        ("いちご", "딸기"), ("ひとつ", "한 개"), ("ふたつ", "두 개")
    ],
    "7과": [
        ("ラーメンや", "라멘 가게"), ("パンや", "빵집"), ("はなや", "꽃집"),
        ("ほんや", "서점"), ("えいが", "영화"), ("ちょっと", "좀, 조금"),
        ("ぜんぜん", "전혀"), ("アクション", "액션"), ("ミュージカル", "뮤지컬"),
        ("バイキング", "바이킹"), ("じゆうじかん", "자유 시간"), ("すみません", "미안합니다, 실례합니다"),
        ("きをつけて", "조심해"), ("しゃしん", "사진"), ("かんらんしゃ", "관람차"),
        ("よじ", "4시"), ("しちじ", "7시"), ("くじ", "9시")
    ],
    "8과": [
        ("うえ", "위"), ("した", "아래"), ("まえ", "앞"), ("うしろ", "뒤"),
        ("となり", "옆"), ("かばん", "가방"), ("つくえ", "책상"), ("みかん", "귤"),
        ("とり", "새"), ("せん", "1,000(천)"), ("やきそば", "야키소바"), ("かきごおり", "빙수"),
        ("りんごあめ", "린고아메"), ("いくら", "얼마"), ("だいじょうぶ", "괜찮아"),
        ("きれい", "예쁘다"), ("あります", "(사물·식물이) 있습니다"), ("います", "(사람·동물이) 있습니다")
    ]
}

UNITS = ["1과", "2과", "3과", "4과", "5과", "6과", "7과", "8과", "전체(1~8과)"]

def get_unit_words(unit_name):
    if unit_name == "1~2과":
        return VOCAB_DATA["1과"] + VOCAB_DATA["2과"]
    if unit_name == "전체(1~8과)":
        all_words = []
        for u in ["1과", "2과", "3과", "4과", "5과", "6과", "7과", "8과"]:
            all_words.extend(VOCAB_DATA[u])
        return all_words
    return VOCAB_DATA.get(unit_name, VOCAB_DATA["1과"])

@st.cache_data(show_spinner=False)
def get_japanese_audio(jp_text):
    tts = gTTS(text=jp_text, lang="ja")
    buf = BytesIO()
    tts.write_to_fp(buf)
    return buf.getvalue()

def make_listening_question(unit_name, exclude_jp=None):
    words = get_unit_words(unit_name)
    candidates = [w for w in words if w[0] != exclude_jp] if exclude_jp and len(words) > 1 else words
    jp, kr = random.choice(candidates)
    return {"jp": jp, "kr": kr}

def make_quiz_question(unit_name, exclude_jp=None):
    words = get_unit_words(unit_name)
    candidates = [w for w in words if w[0] != exclude_jp] if exclude_jp and len(words) > 1 else words
    jp, kr = random.choice(candidates)
    
    wrong_pool = list({w[1] for w in words if w[1] != kr})
    if len(wrong_pool) < 3:
        all_kr = list({w[1] for u in VOCAB_DATA.values() for w in u if w[1] != kr})
        wrong_pool = all_kr
    distractors = random.sample(wrong_pool, 3)
    options = distractors + [kr]
    random.shuffle(options)
    return {"jp": jp, "kr": kr, "options": options}

def make_tile_board(unit_name):
    words = get_unit_words(unit_name)
    unique_kr_words = []
    seen_kr = set()
    shuffled = words[:]
    random.shuffle(shuffled)
    for jp, kr in shuffled:
        if kr not in seen_kr:
            unique_kr_words.append((jp, kr))
            seen_kr.add(kr)
        if len(unique_kr_words) == 6:
            break

    cards = []
    for idx, (jp, kr) in enumerate(unique_kr_words):
        cards.append({"id": f"jp_{idx}", "pair_id": idx, "type": "JP", "text": jp})
        cards.append({"id": f"kr_{idx}", "pair_id": idx, "type": "KR", "text": kr})
    random.shuffle(cards)
    return cards

def fetch_exam_config():
    try:
        res = requests.get(
            GOOGLE_SCRIPT_URL,
            params={"action": "get_config", "_t": int(time.time() * 1000)},
            timeout=5
        )
        data = res.json()
        data["fixed_questions"] = json.loads(data.get("fixed_questions", "[]"))
        return data
    except Exception:
        return {
            "game_type": "타일 매칭 (6쌍)", "unit_name": "1과", "time_limit": 60,
            "mode": "무작위", "fixed_questions": [], "cutline": 12, "is_open": True
        }

def normalize_kst_timestamp(val):
    s = str(val).strip()
    if not s:
        return ""
    try:
        if "T" in s and s.endswith("Z"):
            dt_utc = datetime.fromisoformat(s.replace("Z", "+00:00"))
            dt_kst = dt_utc.astimezone(timezone(timedelta(hours=9)))
            return dt_kst.strftime("%Y-%m-%d %H:%M:%S")
        dt = pd.to_datetime(s)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return s

def fetch_results_df():
    try:
        res = requests.get(
            GOOGLE_SCRIPT_URL,
            params={"action": "get_results", "_t": int(time.time() * 1000)},
            timeout=5
        )
        rows = res.json().get("results", [])
        if len(rows) > 1:
            df = pd.DataFrame(rows[1:], columns=rows[0])
            time_col = df.columns[0]
            df[time_col] = df[time_col].apply(normalize_kst_timestamp)
            return df
        return pd.DataFrame()
    except Exception:
        return pd.DataFrame()

def generate_qr_image(url):
    qr = qrcode.QRCode(box_size=8, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def init_tile_board_from_cfg(cfg, board_idx):
    if cfg["mode"] == "동일 문제" and len(cfg["fixed_questions"]) > 0:
        idx = board_idx % len(cfg["fixed_questions"])
        st.session_state.tile_cards = cfg["fixed_questions"][idx]
    else:
        st.session_state.tile_cards = make_tile_board(cfg["unit_name"])
    st.session_state.matched_pairs = set()
    st.session_state.selected_card_idx = None

def start_attempt(cfg):
    st.session_state.exam_started = True
    st.session_state.start_time = time.time()
    st.session_state.score = 0
    st.session_state.total = 0
    st.session_state.combo = 0
    st.session_state.max_combo = 0
    st.session_state.q_index = 0
    st.session_state.wrong_list = []
    st.session_state.feedback = None
    st.session_state.is_finished = False
    st.session_state.result_sent = False

    if cfg["game_type"] == "타일 매칭 (6쌍)":
        init_tile_board_from_cfg(cfg, 0)
    elif cfg["game_type"] == "원어민 음성 듣고 쓰기":
        if cfg["mode"] == "동일 문제" and len(cfg["fixed_questions"]) > 0:
            st.session_state.current_listen = cfg["fixed_questions"][0]
        else:
            st.session_state.current_listen = make_listening_question(cfg["unit_name"])
    else:
        if cfg["mode"] == "동일 문제" and len(cfg["fixed_questions"]) > 0:
            st.session_state.current_quiz = cfg["fixed_questions"][0]
        else:
            st.session_state.current_quiz = make_quiz_question(cfg["unit_name"])

@st.fragment(run_every=1)
def live_timer_header(time_limit, cutline):
    cutline_text = "없음(연습)" if cutline == 0 else f"{cutline}점"
    m1, m2, m3 = st.columns(3)
    m1.metric("응시자", f"{st.session_state.student_name} ({st.session_state.attempts}차 도전)")
    m2.metric("현재 점수 / 목표", f"{st.session_state.score} / {cutline_text}")

    if time_limit == 0:
        m3.metric("남은 시간", "무제한 ♾️")
    else:
        elapsed = time.time() - st.session_state.start_time
        remaining = max(0, int(time_limit - elapsed))
        if remaining == 0 and not st.session_state.is_finished:
            st.session_state.is_finished = True
            st.rerun()
        mins, secs = divmod(remaining, 60)
        m3.metric("남은 시간", f"{mins:02d}:{secs:02d}")

if "exam_started" not in st.session_state:
    st.session_state.exam_started = False
    st.session_state.attempts = 0

tab_student, tab_teacher = st.tabs(["🎮 학생 단어 게임", "🔐 교사 출제·현황 관리"])

# ==========================================
# [탭 2] 교사 출제 설정 & 실시간 현황 대시보드
# ==========================================
with tab_teacher:
    st.subheader("교사용 단어 게임 관리 센터")
    pw = st.text_input("교사 비밀번호 입력", type="password")
    
    if pw == TEACHER_PASSWORD:
        if "teacher_cfg" not in st.session_state:
            st.session_state.teacher_cfg = fetch_exam_config()
        
        cfg = st.session_state.teacher_cfg
        is_open = bool(cfg.get("is_open", True))

        with st.container(border=True):
            col_status, col_toggle = st.columns([2, 1])
            with col_status:
                if is_open:
                    st.markdown("### 🟢 현재 상태: **게임 진행 중 (오픈됨)**")
                    st.caption("학생들이 접속하여 단어 게임을 진행하고 결과를 제출할 수 있습니다.")
                else:
                    st.markdown("### 🔴 현재 상태: **게임 마감 (잠금됨)**")
                    st.caption("학생 화면이 잠겨 있으며 추가 응시 및 제출이 차단됩니다.")
            with col_toggle:
                st.write("")
                if is_open:
                    if st.button("🔴 지금 게임 마감하기", use_container_width=True):
                        requests.post(GOOGLE_SCRIPT_URL, json={"action": "toggle_open", "is_open": False})
                        st.session_state.teacher_cfg["is_open"] = False
                        st.rerun()
                else:
                    if st.button("🟢 다시 게임 오픈하기", type="primary", use_container_width=True):
                        requests.post(GOOGLE_SCRIPT_URL, json={"action": "toggle_open", "is_open": True})
                        st.session_state.teacher_cfg["is_open"] = True
                        st.rerun()

        st.markdown("#### ⚙️ 새 단어 게임 배포 설정")
        c1, c2 = st.columns(2)
        with c1:
            selected_game = st.radio("1️⃣ 게임 방식 선택", ["타일 매칭 (6쌍)", "4지선다 스피드 퀴즈"])
        with c2:
            selected_mode = st.radio("2️⃣ 출제 방식", ["무작위", "동일 문제"])

        c3, c4 = st.columns(2)
        with c3:
            time_options = [0] + list(range(1, 11))
            selected_min = st.selectbox(
                "3️⃣ 제한 시간",
                time_options,
                index=1,
                format_func=lambda x: "무제한 (연습용)" if x == 0 else f"{x}분"
            )
            time_sec = selected_min * 60
        with c4:
            no_cutline = st.checkbox("4️⃣ 통과 커트라인 없음 (연습용)", value=False)
            if no_cutline:
                cutline_score = 0
                st.info("커트라인: 없음 (0점)")
            else:
                cutline_score = st.number_input("통과 커트라인(점)", min_value=1, max_value=100, value=12, step=1)

        def deploy_unit(u_name, override_game_type=None):
            g_type = override_game_type if override_game_type else selected_game
            fixed_qs = []
            if selected_mode == "동일 문제":
                if g_type == "타일 매칭 (6쌍)":
                    fixed_qs = [make_tile_board(u_name) for _ in range(15)]
                elif g_type == "원어민 음성 듣고 쓰기":
                    fixed_qs = [make_listening_question(u_name) for _ in range(50)]
                else:
                    fixed_qs = [make_quiz_question(u_name) for _ in range(50)]

            payload = {
                "action": "set_config",
                "game_type": g_type,
                "unit_name": u_name,
                "time_limit": time_sec,
                "mode": selected_mode,
                "fixed_questions": fixed_qs,
                "cutline": int(cutline_score),
                "is_open": True
            }
            with st.spinner("배포 중..."):
                requests.post(GOOGLE_SCRIPT_URL, json=payload)
            st.session_state.teacher_cfg = payload
            t_str = "무제한" if selected_min == 0 else f"{selected_min}분"
            c_str = "커트라인 없음" if cutline_score == 0 else f"커트라인 {cutline_score}점"
            st.success(f"✅ 배포 완료! [{u_name} / {g_type} / {t_str} / {selected_mode} / {c_str}]")

        st.write("**5️⃣ 출제할 단원 클릭 (클릭 즉시 오픈 상태로 배포됨):**")
        cols_u1 = st.columns(5)
        for idx in range(5):
            u_name = UNITS[idx]
            if cols_u1[idx].button(f"{u_name} ({len(VOCAB_DATA[u_name])}단어)", key=f"u_btn_{idx}", use_container_width=True):
                deploy_unit(u_name)

        cols_u2 = st.columns(5)
        for idx in range(5, 9):
            u_name = UNITS[idx]
            label = "전체(1~8과)" if u_name == "전체(1~8과)" else f"{u_name} ({len(VOCAB_DATA[u_name])}단어)"
            if cols_u2[idx - 5].button(label, key=f"u_btn_{idx}", use_container_width=True):
                deploy_unit(u_name)

        if cols_u2[4].button("🔊 원어민 발음 듣고 쓰기 (1~2과)", key="u_btn_listen_1_2", type="primary", use_container_width=True):
            deploy_unit("1~2과", override_game_type="원어민 음성 듣고 쓰기")

        st.divider()

        with st.expander("📱 학생 접속용 QR코드 크게 보기 (칠판/TV 띄우기용)"):
            col_qr1, col_qr2 = st.columns([1, 2])
            with col_qr1:
                st.image(generate_qr_image(APP_PUBLIC_URL), width=200)
            with col_qr2:
                st.markdown("#### 스마트폰 카메라로 QR코드를 스캔하세요!")
                st.code(APP_PUBLIC_URL)
                st.caption("※ 코드 상단의 APP_PUBLIC_URL 변수에 실제 배포된 주소를 입력하면 해당 주소의 QR코드가 생성됩니다.")

        st.markdown("#### 📊 실시간 통과(제출) 현황 및 화면 정리")
        col_ref, col_new = st.columns(2)
        with col_ref:
            if st.button("🔄 최신 제출 명단 새로고침", use_container_width=True):
                st.toast("최신 명단을 불러왔습니다!")
                st.rerun()
        with col_new:
            if st.button("✨ 새 반 시작 (화면만 비우기)", type="primary", use_container_width=True):
                kst = timezone(timedelta(hours=9))
                st.session_state.view_after = datetime.now(kst).strftime("%Y-%m-%d %H:%M:%S")
                st.toast("새 반 화면으로 초기화되었습니다!")
                st.rerun()

        df_res = fetch_results_df()
        if not df_res.empty and "view_after" in st.session_state:
            time_col = df_res.columns[0]
            df_res = df_res[df_res[time_col] > st.session_state.view_after]

        if not df_res.empty:
            st.metric("현재 화면 통과 인원", f"{len(df_res)}명")
            st.dataframe(df_res.iloc[::-1], use_container_width=True, hide_index=True)

            csv_data = df_res.to_csv(index=False).encode("utf-8-sig")
            kst = timezone(timedelta(hours=9))
            file_time = datetime.now(kst).strftime("%Y%m%d_%H%M")
            st.download_button(
                label="📥 현재 화면 결과 엑셀(CSV)로 다운로드",
                data=csv_data,
                file_name=f"단어게임결과_{file_time}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("현재 표시할 통과 기록이 없습니다. (기존 누적 데이터는 구글 시트에 안전하게 보관되어 있습니다)")

    elif pw:
        st.error("비밀번호가 올바르지 않습니다.")

# ==========================================
# [탭 1] 학생 게임 응시 화면
# ==========================================
with tab_student:
    st.title("🇯🇵 생활일본어 단어 게임")

    if not st.session_state.exam_started:
        if "config" not in st.session_state:
            st.session_state.config = fetch_exam_config()
        
        cfg = st.session_state.config
        is_open = bool(cfg.get("is_open", True))

        if not is_open:
            st.warning("🔒 현재 선생님이 게임을 마감하여 진행 중인 활동이 없습니다.")
            if st.button("🔄 오픈 여부 다시 확인하기"):
                st.session_state.config = fetch_exam_config()
                st.rerun()
        else:
            t_limit = int(cfg["time_limit"])
            time_display = "무제한 (연습용)" if t_limit == 0 else f"{t_limit // 60}분"
            cutline = int(cfg.get("cutline", 0))
            cutline_display = "없음 (자유 연습)" if cutline == 0 else f"{cutline}점 이상 (미달 시 재도전)"

            with st.container(border=True):
                st.markdown("### 📌 현재 배포된 단어 게임 안내")
                st.write(f"- **출제 단원:** {cfg['unit_name']}")
                st.write(f"- **게임 방식:** **{cfg['game_type']}**")
                st.write(f"- **제한 시간:** {time_display}")
                st.write(f"- **출제 방식:** {cfg['mode']}")
                st.write(f"- **통과 기준(커트라인):** **{cutline_display}**")
                if cfg["game_type"] == "원어민 음성 듣고 쓰기":
                    st.caption("🎧 팁: 소리를 잘 듣고 스마트폰의 일본어 키보드로 정확히 입력해 주세요!")
                if st.button("🔄 최신 출제 설정 새로고침"):
                    st.session_state.config = fetch_exam_config()
                    st.rerun()

            st.subheader("응시자 정보 입력")
            c1, c2 = st.columns(2)
            s_id = c1.text_input("학번 (예: 10215)")
            s_name = c2.text_input("이름 (예: 홍길동)")

            if st.button("🚀 게임 시작하기", type="primary", use_container_width=True):
                if not s_id.strip() or not s_name.strip():
                    st.warning("학번과 이름을 모두 입력해 주세요!")
                else:
                    st.session_state.student_id = s_id.strip()
                    st.session_state.student_name = s_name.strip()
                    st.session_state.attempts = 1
                    start_attempt(cfg)
                    st.rerun()

    else:
        cfg = st.session_state.config
        time_limit = int(cfg["time_limit"])
        cutline = int(cfg.get("cutline", 0))

        if time_limit > 0 and (time.time() - st.session_state.start_time) >= time_limit and not st.session_state.is_finished:
            st.session_state.is_finished = True

        # ------------------------------------------
        # 게임 종료 및 결과 처리 화면
        # ------------------------------------------
        if st.session_state.is_finished:
            cutline_text = "없음(연습)" if cutline == 0 else f"{cutline}점"
            time_end_text = "무제한" if time_limit == 0 else "00:00"
            m1, m2, m3 = st.columns(3)
            m1.metric("응시자", f"{st.session_state.student_name} ({st.session_state.attempts}차 도전)")
            m2.metric("최종 점수 / 목표", f"{st.session_state.score} / {cutline_text}")
            m3.metric("남은 시간", time_end_text)
            st.divider()

            is_passed = st.session_state.score >= cutline

            if is_passed:
                if not st.session_state.result_sent:
                    kst = timezone(timedelta(hours=9))
                    now_str = datetime.now(kst).strftime("%Y-%m-%d %H:%M:%S")
                    acc = round((st.session_state.score / st.session_state.total * 100), 1) if st.session_state.total > 0 else 0
                    t_record = "무제한" if time_limit == 0 else f"{time_limit // 60}분"
                    
                    payload = {
                        "action": "submit_result",
                        "timestamp": now_str,
                        "student_id": st.session_state.student_id,
                        "student_name": st.session_state.student_name,
                        "game_type": cfg["game_type"],
                        "unit_name": cfg["unit_name"],
                        "mode": cfg["mode"],
                        "time_text": t_record,
                        "score": st.session_state.score,
                        "total": st.session_state.total,
                        "accuracy": f"{acc}%",
                        "attempts": f"{st.session_state.attempts}회"
                    }
                    with st.spinner("통과! 선생님 구글 시트로 결과를 전송하는 중입니다..."):
                        requests.post(GOOGLE_SCRIPT_URL, json=payload)
                    st.session_state.result_sent = True

                st.balloons()
                st.success(f"🎉 통과했습니다! **{st.session_state.student_name}** 학생, 총 **{st.session_state.score}점**으로 선생님께 기록이 전송되었습니다! (총 {st.session_state.attempts}차 시도)")

                if st.button("🔄 한 번 더 연습하기", use_container_width=True):
                    st.session_state.attempts += 1
                    start_attempt(cfg)
                    st.rerun()

            else:
                st.error(f"💦 아쉽습니다! 현재 **{st.session_state.score}점**으로 통과 기준(**{cutline}점**)에 도달하지 못했습니다. 결과가 전송되지 않았으니 다시 도전하세요!")

                if st.button("🔄 다시 도전하기", type="primary", use_container_width=True):
                    st.session_state.attempts += 1
                    start_attempt(cfg)
                    st.rerun()

            if st.session_state.wrong_list:
                st.subheader("📝 방금 틀린 단어 복습")
                for w_jp, w_kr, u_input in st.session_state.wrong_list:
                    st.write(f"- **{w_jp}** ({w_kr}) → 내 입력: `{u_input}`")

        # ------------------------------------------
        # 게임 진행 화면
        # ------------------------------------------
        else:
            live_timer_header(time_limit, cutline)

            if cutline > 0:
                prog_val = min(st.session_state.score / cutline, 1.0)
                st.progress(prog_val, text=f"목표 달성률: {int(prog_val * 100)}% (남은 점수: {max(0, cutline - st.session_state.score)}점)")
            else:
                st.info("♾️ **자유 연습 모드**입니다. 원하는 만큼 연습한 뒤 아래 **[⏹️ 지금 종료하고 결과 확인하기]** 버튼을 누르세요.")

            if st.session_state.feedback:
                f_type, f_msg = st.session_state.feedback
                if f_type == "success":
                    st.success(f_msg)
                else:
                    st.error(f_msg)

            # [게임 모드 A] 타일 매칭 (6쌍 짝맞추기)
            if cfg["game_type"] == "타일 매칭 (6쌍)":
                st.caption("일본어 카드와 알맞은 한글 뜻 카드를 차례로 클릭해 짝을 맞추세요! (1쌍 성공 = +1점)")
                cards = st.session_state.tile_cards
                matched = st.session_state.matched_pairs
                sel_idx = st.session_state.selected_card_idx

                for row in range(4):
                    cols = st.columns(3)
                    for col in range(3):
                        idx = row * 3 + col
                        card = cards[idx]
                        is_matched = card["pair_id"] in matched
                        is_selected = (sel_idx == idx)

                        if is_matched:
                            cols[col].button(f"✅ {card['text']}", key=f"tile_{idx}_{st.session_state.q_index}", disabled=True, use_container_width=True)
                        else:
                            btn_type = "primary" if is_selected else "secondary"
                            if cols[col].button(card["text"], key=f"tile_{idx}_{st.session_state.q_index}", type=btn_type, use_container_width=True):
                                if sel_idx is None:
                                    st.session_state.selected_card_idx = idx
                                    st.rerun()
                                elif sel_idx == idx:
                                    st.session_state.selected_card_idx = None
                                    st.rerun()
                                else:
                                    first_card = cards[sel_idx]
                                    st.session_state.total += 1
                                    if first_card["pair_id"] == card["pair_id"] and first_card["type"] != card["type"]:
                                        st.session_state.score += 1
                                        st.session_state.matched_pairs.add(card["pair_id"])
                                        st.session_state.selected_card_idx = None
                                        jp_txt = first_card["text"] if first_card["type"] == "JP" else card["text"]
                                        kr_txt = card["text"] if first_card["type"] == "JP" else first_card["text"]
                                        st.session_state.feedback = ("success", f"⭕ 짝맞추기 성공! ({jp_txt} = {kr_txt})")

                                        if len(st.session_state.matched_pairs) == 6:
                                            st.session_state.q_index += 1
                                            init_tile_board_from_cfg(cfg, st.session_state.q_index)
                                            st.session_state.feedback = ("success", "🎉 6쌍 모두 클리어! 새로운 카드 12장이 열렸습니다!")
                                        st.rerun()
                                    else:
                                        st.session_state.selected_card_idx = None
                                        st.session_state.feedback = ("error", f"❌ 짝이 맞지 않습니다! ({first_card['text']} ≠ {card['text']})")
                                        st.rerun()

            # [게임 모드 B] 원어민 음성 듣고 쓰기 (1~2과)
            elif cfg["game_type"] == "원어민 음성 듣고 쓰기":
                if st.session_state.combo >= 3:
                    st.info(f"🔥 **{st.session_state.combo}연속 정답 행진 중!**")

                listen_q = st.session_state.current_listen
                with st.container(border=True):
                    st.markdown("#### 🎧 원어민 발음을 듣고 일본어로 입력하세요")
                    audio_bytes = get_japanese_audio(listen_q["jp"])
                    st.audio(audio_bytes, format="audio/mp3", autoplay=True)
                    st.caption("※ 자동 재생이 안 될 경우 재생 버튼(▶)을 눌러 여러 번 다시 들을 수 있습니다.")

                with st.form(key="listening_form", clear_on_submit=True):
                    jp_input = st.text_input("일본어(히라가나) 입력:", placeholder="예: すし, ありがとう")
                    submitted = st.form_submit_button("✅ 정답 제출", type="primary", use_container_width=True)

                if submitted:
                    cleaned_jp = jp_input.replace(" ", "").replace(" ", "").strip()
                    st.session_state.total += 1
                    if cleaned_jp == listen_q["jp"]:
                        st.session_state.score += 1
                        st.session_state.combo += 1
                        st.session_state.max_combo = max(st.session_state.max_combo, st.session_state.combo)
                        st.session_state.feedback = ("success", f"⭕ 정답! ({listen_q['jp']} : {listen_q['kr']})")
                    else:
                        st.session_state.combo = 0
                        st.session_state.feedback = ("error", f"❌ 오답! 정답은 '{listen_q['jp']}' ({listen_q['kr']}) 입니다. (내 입력: {cleaned_jp})")
                        st.session_state.wrong_list.append((listen_q["jp"], listen_q["kr"], cleaned_jp))

                    st.session_state.q_index += 1
                    if cfg["mode"] == "동일 문제" and len(cfg["fixed_questions"]) > 0:
                        idx = st.session_state.q_index % len(cfg["fixed_questions"])
                        st.session_state.current_listen = cfg["fixed_questions"][idx]
                    else:
                        st.session_state.current_listen = make_listening_question(cfg["unit_name"], exclude_jp=listen_q["jp"])
                    st.rerun()

            # [게임 모드 C] 4지선다 스피드 퀴즈
            else:
                if st.session_state.combo >= 3:
                    st.info(f"🔥 **{st.session_state.combo}연속 정답 행진 중!**")

                quiz = st.session_state.current_quiz
                with st.container(border=True):
                    st.markdown(
                        f"<div style='text-align: center; font-size: 64px; font-weight: bold; padding: 20px;'>{quiz['jp']}</div>",
                        unsafe_allow_html=True
                    )

                st.write("**알맞은 한글 뜻을 선택하세요:**")
                opt_cols = st.columns(2)
                for i, opt in enumerate(quiz["options"]):
                    if opt_cols[i % 2].button(f"{i+1}. {opt}", key=f"opt_{i}_{st.session_state.q_index}", use_container_width=True):
                        st.session_state.total += 1
                        if opt == quiz["kr"]:
                            st.session_state.score += 1
                            st.session_state.combo += 1
                            st.session_state.max_combo = max(st.session_state.max_combo, st.session_state.combo)
                            st.session_state.feedback = ("success", f"⭕ 정답! ({quiz['jp']} = {opt})")
                        else:
                            st.session_state.combo = 0
                            st.session_state.feedback = ("error", f"❌ 오답! '{quiz['jp']}'의 뜻은 '{quiz['kr']}'입니다. (내 선택: {opt})")
                            st.session_state.wrong_list.append((quiz["jp"], quiz["kr"], opt))

                        st.session_state.q_index += 1
                        if cfg["mode"] == "동일 문제" and len(cfg["fixed_questions"]) > 0:
                            idx = st.session_state.q_index % len(cfg["fixed_questions"])
                            st.session_state.current_quiz = cfg["fixed_questions"][idx]
                        else:
                            st.session_state.current_quiz = make_quiz_question(cfg["unit_name"], exclude_jp=quiz["jp"])
                        st.rerun()

            st.divider()
            if st.button("⏹️ 지금 종료하고 결과 확인하기", use_container_width=True):
                st.session_state.is_finished = True
                st.rerun()
