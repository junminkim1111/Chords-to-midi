import json
import re
import threading 
import asyncio, sys
from queue import Queue 
from google import genai
from google.genai import types
from playwright.sync_api import sync_playwright
import pretty_midi
from pychord import Chord
from config import Config

class MusicToMidiAgent:
    def __init__(self, url,api_key):
        if not api_key:
            raise ValueError("The API key is missing. Please set it in the .env file.")
        self.client = genai.Client(api_key=api_key)
        self.url = url

    def get_Song_name(self):
        if '-chords-' in self.url:
            return self.url.split('/')[-1].split('-chords-')[0]
        return "Unknown"

    def fetch_tab(self):
        print(f"🌐 Fetching data from: {self.url}...")
        
        result_queue = Queue()

        def run_playwright():
            if sys.platform.startswith("win"):
                try:
                    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
                except:
                    pass

            try:
                with sync_playwright() as p:

                    browser = p.chromium.launch(headless=True)
                    
                    context = browser.new_context()
                    
                    page = context.new_page()

                    
                    page.route("**/*", lambda route: route.abort() 
                        if route.request.resource_type in ["image", "media", "font"] 
                        else route.continue_())

                    try:
                        # 페이지 이동
                        page.goto(self.url, wait_until="domcontentloaded", timeout=60000)
                    except Exception:
                        print("⚠️ loading took too long, trying to continue...")

                    page.wait_for_timeout(2000) 

                    # 데이터 추출
                    tab_content = page.evaluate("""
                        () => {
                            try { return window.UGAPP.store.page.data.tab_view.wiki_tab.content; }
                            catch (e) { return null; }
                        }
                    """)

                    if tab_content:
                        clean = tab_content.replace('[tab]', '').replace('[/tab]', '').replace('[ch]', '').replace('[/ch]', '')
                        result_queue.put(clean)
                    else:
                        try:
                            content = page.locator("pre, .js-tab-content, code").first.inner_text()
                            result_queue.put(content)
                        except:
                            result_queue.put(None)
                    
                    browser.close()

            except Exception as e:
                print(f"❌ Thread Error: {e}")
                result_queue.put(None)

        t = threading.Thread(target=run_playwright)
        t.start()
        t.join() 
        
        return result_queue.get()

    def analyze(self, text):
        print("🧠 Analyzing with Gemini...")
        prompt = f"""
        Analyze the guitar tab text below.
        Input: {text[:10000]}
        Requirements:
        1. Title: Song title.
        2. BPM: Estimate tempo (default {Config.DEFAULT_BPM}).
        3. Chords: Sequence.
        4. Beats: Duration.
        """
        try:
            response = self.client.models.generate_content(
                model=Config.MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema={
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "bpm": {"type": "integer"},
                            "chords": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "chord": {"type": "string"},
                                        "beats": {"type": "integer"}
                                    }
                                }
                            }
                        }
                    }
                )
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"❌ Analysis Error: {e}")
            return None

    def compose(self, song_data, user_bpm=None, custom_filename=None):

        if custom_filename and custom_filename.strip():
            safe_name = self._sanitize_filename(custom_filename)
            filename = f"{safe_name}.mid"
        else:
            title = self._sanitize_filename(self.get_Song_name())
            filename = f"{title}.mid"

        print(f"🎹 Composing: {filename}...")
        midi = pretty_midi.PrettyMIDI()
        piano = pretty_midi.Instrument(program=Config.DEFAULT_INSTRUMENT)
        
        bpm = int(user_bpm) if user_bpm else song_data.get("bpm", Config.DEFAULT_BPM)
        seconds_per_beat = 60 / bpm
        current_time = 0.0

        for item in song_data.get("chords", []):
            try:
                chord_name = item["chord"].split('/')[0]
                beats = item["beats"]
                duration = beats * seconds_per_beat
                
                c = Chord(chord_name)
                for char_note in c.components():
                    note_num = pretty_midi.note_name_to_number(f"{char_note}4")
                    note = pretty_midi.Note(velocity=100, pitch=note_num, start=current_time, end=current_time + duration)
                    piano.notes.append(note)
                
                current_time += duration
            except Exception:
                pass 

        midi.instruments.append(piano)
        midi.write(filename)
        print(f"✅ Success! Saved as {filename}")
        return filename

    def _sanitize_filename(self, name):
        return re.sub(r'[\\/*?:"<>|]', "", name).strip().replace(" ", "_")