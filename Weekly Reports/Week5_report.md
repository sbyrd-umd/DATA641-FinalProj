---
team: Inflection
week: 5
date: 2026-7-1
members:
  - name: Alessandro Vivaldi
    github: xandrov1
    hat: Product | Engineering | Data&Eval
  - name: Andrew Liu
    github: AndrewLiu-1
    hat: Product | Engineering | Data&Eval
  - name: Sawyer Byrd
    github: sawyerbyrd
    hat: Product | Engineering | Data&Eval
north_star:
  metric: Working translation layer
  value: working
  previous: Hone concept and idea and start structuring
---

## Shipped this week
- This week we were able to started building the foundations of our product. We deveoped a script that captures audio from the microphone, streams it to the Deepgram API for real-time transcription, and translates the returned transcript to English using the Google Translate Python library. Then both the original transcript and the English translation are printed to the terminal for review.
- The transcribe script uses threading to keep latency as low as possible, and Deepgram's streaming API handles transcription with minimal delay.
- We are also implementing a automatic live language detection, which is able to detect the spoken language per transcript chunk live.

### Current program flow:
1. The user runs our transcribe script and selects a source language from the available list
2. A deepgram connect opens with that language set
3. Then any micropphone audio streams to Deepgram which is able to output text chunks from the transcript in the source language in real time (as JSON)
4. Each outputted chunk from the transcript is sent to the Google Translate library to be translated to English
5. Finally, the original transcript in the source language and the English translation are printed to the terminal

## This Week's Updates
- Our first task was to decide the best transcription option for our project and landed on Deepgram, which provides streaming/real-time transcription through an API and has already addressed the latency concerns we had discussed with the professor in last week's meeting.
- For translation, we compared the Google Translate Python library against DeepL. Google Translate requires no API key setup (just a library import) and covers 130+ languages. DeepL is higher quality but supports only ~30 languages and its free tier (500,000 characters/month) would likely be exhausted too quickly for our use. We went with Google Translate for now.
- Deepgram is capable of translating on its own, however it returns only the translated transcript and not the original like we want. For now, we want to include both the original and translated transcripts, so that we can see if we lose any emotional or tonal information through the sentiment analysis.

## Challenges / blockers
- Capturing system audio (what comes out of the speakers, not just the mic) varies significantly by operating system. For now we are building the tool for Windows first, but we may need to implement separate versions for different operating systems down the line.

## Next week's goal

## Individual contributions
- Alessandro Vivaldi (Engineer): Researched and compared transcription and translation options, and built the working real-time transcription and translation script .
- Sawyer Byrd (Engineer): Implemented and tested our live automatic language detection feature
- Andrew Liu (Organizer): Helped organize our research information and ideas in a clean format that we can keep track of.

