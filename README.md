# Chords-to-midi
Ultimite Guitar URL을 가져와서 gemini가 코드진행을 분석 한 뒤 이를 midi 블럭으로 만드는 python 파일

1. 필수 라이브러리 설치
   '''
  pip install streamlit google-genai playwright pretty_midi pychord
  playwright install'''

2. 앱 실행
   '''
   streamlit run app.py'''
   
3. Google Gemini API 키 입력
웹 페이지 왼쪽 **사이드바(Sidebar)**를 확인합니다.

"Google Gemini API Key" 입력창에 API 키를 입력합니다.

키가 없다면 Google AI Studio에서 무료로 발급받을 수 있습니다.

엔터를 치면 키가 적용됩니다.

4. 변환하기
링크 입력: 메인 화면의 입력창에 변환하고 싶은 Ultimate Guitar 탭 URL을 붙여넣습니다.

예시: https://tabs.ultimate-guitar.com/tab/artist/song-chords-12345

설정 (선택 사항):

BPM: 0으로 두면 AI가 자동 추정하며, 숫자를 입력하면 그 속도로 고정됩니다.

파일 이름: 원하는 파일명을 입력합니다 (비워두면 곡 제목으로 저장됨).

변환 시작: 🎵 MIDI 변환 시작 버튼을 클릭합니다.

5. 결과 확인
진행 상황(데이터 수집 -> AI 분석 -> MIDI 생성)이 화면에 표시됩니다.

완료되면 💾 다운로드 버튼이 나타납니다. 클릭하여 .mid 파일을 저장하세요.
