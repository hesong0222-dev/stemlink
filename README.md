<p align="center"><img src="mascot.png" width="140"></p>

# stemlink

유튜브 링크 붙여넣으면 **보컬 · 드럼 · 베이스 · 나머지** 4트랙으로 나눠주는 앱.

서버 없음. **내 컴퓨터에서** 돌아감 (맥 M칩 GPU / 엔비디아 GPU / 없으면 CPU 자동 선택).
10분짜리 영상이 M4 맥북 에어에서 85초 걸렸어요.

## 실행

[uv](https://docs.astral.sh/uv/)랑 ffmpeg만 있으면 한 줄:

```bash
uvx --python 3.12 --from git+https://github.com/hesong0222-dev/stemlink stemlink
```

브라우저가 열리면 링크 넣고 "나누기". 처음 한 번은 분리 모델(약 80MB) 받느라 조금 더 걸림.

- 결과 저장 위치: `~/Music/stemlink/`
- 포트 바꾸기: `STEMLINK_PORT=8000`

<details><summary>uv, ffmpeg 없으면</summary>

```bash
# 맥
brew install uv ffmpeg
# 윈도우
winget install astral-sh.uv Gyan.FFmpeg
```
</details>

## 어떻게 돌아가냐면

1. [yt-dlp](https://github.com/yt-dlp/yt-dlp)로 소리만 받음
2. [Demucs](https://github.com/facebookresearch/demucs) (htdemucs 모델)로 4트랙 분리
3. 브라우저에서 바로 듣고 mp3로 받기

## 주의

본인이 권리를 가진 음원이나, 개인 연습·공부 용도로만 쓰세요. 받은 음원 재배포는 저작권 위반일 수 있어요.

---

MIT · 만든 사람 [개발새발자](https://x.com/ComAsNas)
