# Choosing a transcription and alignment route

Model names and capabilities change. When making a recommendation, check each provider’s current official model and language pages. Treat the options below as candidates to evaluate, not a fixed ranking or guarantee of Moroccan Darija accuracy.

## Candidate routes

| Provider or tool | Current documented route to evaluate | What to check for this clip |
|---|---|---|
| OpenAI API | Current recommended file-transcription model; current docs distinguish it from the `whisper-1` path for word timestamps. | Test Darija and code-switch recognition. If the chosen transcript model does not return reliable word times, align it separately. [Transcription docs](https://developers.openai.com/api/docs/guides/transcription) |
| Google Gemini API | `gemini-3.5-transcribe` provides verbatim mode and optional word timestamp granularity; automatic language detection supports code-switching. | Test Darija script and French/English switches. Word timestamps can reduce transcription accuracy; custom vocabulary cannot be combined with word timestamps. [Gemini transcription docs](https://ai.google.dev/gemini-api/docs/transcribe) |
| Microsoft Foundry Speech | `MAI-Transcribe-2` documents verbatim output, code-switching, automatic language ID, and word timestamps; public preview status and language/region access can change. | Confirm current `ar-MA` support, preview availability, region, and whether the exact mixed audio is handled well. [MAI-Transcribe docs](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/mai-transcribe), [language support](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support) |
| AssemblyAI | Current Universal pre-recorded models document broad language coverage and code-switching; the current Pro line’s listed language coverage changes over time. | Verify pre-recorded model coverage for Arabic, French, and English, and test Moroccan dialect/script. Check the API response’s timing granularity. [Models](https://www.assemblyai.com/docs/getting-started/models) |
| Deepgram | Nova-3 lists Arabic Morocco (`ar-MA`) and provides general-purpose speech recognition. | The documented multilingual mode may list a different language set from the Arabic locale route. Check the current language page and test mixed Arabic/French/English rather than assuming code-switch behavior. [Models and languages](https://developers.deepgram.com/docs/models-languages-overview/) |
| Local MoulSot | Atlasia's `moulsot.v0.3` is a Darija-focused ASR candidate with stated support for code-switching; its model card documents CUDA/PyTorch and Apple Silicon/MLX use. | Treat the model-card results as the publisher's claims, not a guarantee for this speaker. Check the current model size, license, runtime requirements, supported script, and output timestamps before offering installation. It is a text recognizer; align reviewed output separately if it does not provide reliable word times. [MoulSot model card](https://huggingface.co/atlasia/moulsot.v0.3) |
| Local Whisper models | Multilingual Whisper checkpoints can run through implementations such as `faster-whisper`; the runtime offers CPU `int8`, supported GPU modes, and optional word timestamps. | Pick a checkpoint and runtime to fit the user's actual hardware and languages. Smaller/faster is a tradeoff to compare, not a guarantee of acceptable Darija accuracy. [faster-whisper](https://github.com/SYSTRAN/faster-whisper) |
| Local WhisperX | Whisper-based ASR plus voice activity detection and forced alignment; it can also align reviewed text supplied by another recognizer. | Confirm device/runtime requirements and alignment-model coverage for Arabic, French, and English. Multi-language words may need separate alignment spans and human review. [WhisperX](https://github.com/m-bain/whisperX) |

Other providers can be added when their current official documentation confirms useful language and timing support. Do not keep a stale “best models” table as if it were a benchmark.

## Selection method

When the user asks for the best option:

1. Ask their constraints: an existing local model, OS and hardware, data privacy, local vs cloud, cost, time, word timestamps, and whether they want to test a short excerpt.
2. For local use, inspect available hardware and installed runtimes without running inference. Check the current model card and runtime requirements for the exact model, quantization, and operating system; estimate storage before offering a download.
3. Check current official/provider docs for model IDs, supported languages/locales, timestamp granularity, code-switch claims, file limits, availability, and pricing. Do not expose provider keys.
4. Offer a short list of suitable candidates with specific tradeoffs for Arabic/Moroccan dialect plus French/English. Avoid vendor accuracy claims unless they apply to a comparable test.
5. Ask before installing packages or model weights, spending money, or uploading private audio to a new provider. If authorized, compare a representative excerpt containing Darija, French, English, names, and language switches.
6. Review candidate transcripts against the audio. Compare word omissions/substitutions, script choice, fillers, named terms, language switches, and timestamp reliability. A vendor's generic benchmark is not proof of performance on this speaker.
7. Choose transcription and alignment independently. A local text model such as MoulSot can be paired with WhisperX or another compatible aligner; a local Whisper runtime may provide word estimates, which still need review.

## Keep the roles distinct

- **Speech recognition (ASR):** predicts the words from audio.
- **Forced alignment:** takes a reviewed transcript and estimates when its words occur in the audio.
- **WhisperX:** a local Whisper-based ASR and alignment toolkit; it can also align an external transcript. It is not the same category as a hosted Gemini/OpenAI/Deepgram transcription endpoint.
- **Local processing:** keeps inference on the creator's computer only when the selected runtime is configured locally. Model setup may still fetch code and weights from the provider; verify the runtime's data behavior and ask before downloading.
- **Video editor:** HyperFrames or Remotion places the reviewed words and their times into a renderable composition.
