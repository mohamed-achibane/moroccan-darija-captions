# One-time project intake

Run this intake once before editing. First inspect the current request and project so the user does not need to repeat information they already supplied. Ask all remaining questions together, then carry the answers through delivery without asking for the same approval again.

## 1. Read-only capability and credential discovery

Use only tools already available in the active assistant environment. Before asking the user to choose a speech route, perform a scoped, read-only inventory of resources relevant to this video:

- Confirm the source video, existing project, output location, and whether the active environment can access them.
- Read relevant project instructions and inspect the existing composition/source-of-truth structure so the intake names the actual editor, delivery files, and planned media actions.
- Identify installed transcription and alignment runtimes, usable local models, and cached model files. Do not run inference during discovery.
- Check OS, architecture, available memory, accelerator, and free disk when local inference or an installation may be relevant.
- Identify available editors, render tools, and fonts when the environment can inspect them.
- Check whether supported provider credentials appear configured through the active environment's documented credential store or relevant environment-variable names. Report provider and presence only; treat it as unverified until an authorized request succeeds. Perform only a silent presence check: never reveal, print, log, or copy secret values, dump the environment, or search unrelated files or the whole disk for keys.
- Check current official provider documentation for applicable speech models, supported timing output, audio limits, and pricing. Do not make a paid request or upload audio as part of discovery.

If the assistant surface cannot inspect the computer, say which checks are unavailable. Do not claim a local model or key exists based on the assistant brand, subscription, or a prior task. A detected credential only means it may be configured; it does not prove validity or authorize sending audio or spending money. Do not verify a credential with a provider request until that provider use is authorized.

## 2. Show findings, then ask once

Give a short summary of the findings: usable local ASR/alignment tools, provider credential availability (never values), relevant current API choices, estimated upload/API cost, any required installs and model sizes, editor access, and any unknowns. Recommend one route for this clip with a brief tradeoff. Treat language-support claims as candidates, not proof of Moroccan Darija accuracy.

Then ask one bundled intake containing only choices not already answered in the request or project:

> **Speech route:** Shall I use **[recommended current API/model]**, **[available local ASR model]**, or install **[local ASR runtime/model and size]**? If I use **[provider]**, may I send this clip's **audio** to that provider and spend up to **[estimated amount or user-set cap]**? For word timing, may I use **[provider timestamps/existing aligner]** or install **[aligner packages and model names/sizes]**? A detected API key is not permission to use it. I will never ask you to paste a key.
>
> **Caption appearance:** Would you like captions to show **one word at a time (default)** or **two consecutive words at a time**, with the spoken word highlighted? What color should the captions use? A color name or HEX value is fine. If you choose two words and provide one color, apply it to the spoken word and keep the following word in the house-style secondary color unless you request another color. If you do not specify a color, use the house-style colors.
>
> **Project and destination:** I found **[editor/existing project]** and will deliver **[editable project and fresh MP4]** to **[folder/name]**, using the approved house style unless you already supplied another style. If no editor is already clear, do you prefer HyperFrames or Remotion? If no output location is clear, where should I save the project and MP4?
>
> **End-to-end authorization:** Do you authorize me to review the full audio and transcript, create the editable composition, open and review the editor preview/Studio when available, run the relevant media checks, build, render a fresh MP4, and inspect the final video and audio—all in this task without asking again at each step? If words remain genuinely unclear after review, should I pause for your help or render a clearly marked review draft?

The ecosystem-specific speech prompts below replace the generic **Speech route** wording above; they are not extra questions. Keep the complete intake to one message and omit any choice already answered, including caption word count or color already specified in the request or project. If caption appearance is unanswered, proceed with one word at a time and the house-style colors after presenting the choice; do not block the task solely for a missing style preference.

Do not ask about a source, destination, editor, style, provider, or action the user has already clearly specified. When a user asks for a recommendation, recommend one option from the discovered tools and current documentation rather than asking them to compare a long vendor list.

### Ecosystem-specific speech choices

The assistant ecosystem selects the entry skill, not automatically the speech provider. Use the matching adapter and offer the ecosystem's provider only when current official docs and available credentials confirm a suitable audio-transcription route.

- **Codex or ChatGPT:** Ask: “For speech recognition, should I use OpenAI’s current documented **[transcription model]**, or the available local **[model]**? OpenAI documents **[word-timing option]** for timestamps; the transcript and timing models may differ. May I send this clip’s extracted audio to OpenAI and spend up to **[cap]**?” Offer OpenAI only when the relevant docs and credential presence support it. A ChatGPT subscription does not imply OpenAI API access.
- **Gemini:** Ask: “For speech recognition, should I use Gemini’s current documented **[transcription model]**, or the available local **[model]**? Gemini documents **[word-timestamp option and any accuracy caveat]**. May I send this clip’s extracted audio to Google and spend up to **[cap]**?” Offer Gemini only when the relevant docs and credential presence support it.
- **Claude:** Check current official Anthropic documentation. If it does not document a suitable speech-to-text endpoint, say: “I couldn’t confirm a Claude speech-to-text route for this task. Would you prefer the available local **[model]**, or should I use **[named external API]** with your permission to upload the audio and spend up to **[cap]**?” Claude can still be the assistant used for the rest of the workflow.
- **Local-first or another ecosystem:** Ask: “The available local speech model is **[model]**. Should I use it to keep audio on this device, or use **[named API]**? The API would receive the extracted audio and may cost up to **[cap]**.” Offer an API only when the user authorizes that provider, its audio upload, and its cost.

Append the word-alignment choice to the same question: name provider timestamps and their tradeoffs, an existing local aligner, or any proposed aligner packages/models and their approximate download size. If an ASR model also needs installing, name and size it separately. Ask for explicit consent for each cloud upload/cost and each new local install/download; never infer consent from the route choice alone.

Ask for a cost ceiling before a paid API request, and name the provider and data being sent. If cost cannot be estimated before the request, do not make the request until the user approves a clear cap. Ask for package/model installation consent only after naming the exact items and approximate total download/storage needs. Do not silently switch providers, send media to another service, or install additional tools when a route fails.

For an authorized local install, prefer an isolated environment and avoid administrator-level changes. Confirm the selected local runtime will not upload audio. Do not exceed the named package/model list or download size without asking again.

If the user selects an API but no matching credential appears configured, say that the API route is unavailable until they configure credentials through the provider's supported secret store. Offer an already available local route if one exists. Never ask the user to paste a key into chat, a prompt, a project file, or source control.

## 3. Carry consent through the task

- Treat explicit consent in this intake as permission for the named actions in this video task. Do not repeat per-action approval requests for the same authorized checks, preview, build, or render.
- Stop and ask only when a needed action falls outside the stated provider, cost, upload, install, or render scope; a required fact is missing; or an unresolved transcript choice would materially affect the words shown.
- If the authorized tools cannot supply reliable word timings and the user did not authorize a suitable aligner, explain the limit and stop before presenting the video as finished. Never switch providers, guess timings, or silently install a model to get past the blocker.
- Never fabricate unclear words or timings. If the user chose a flagged review draft, label unresolved spans and do not call that render publish-ready. If the user chose to pause, wait for their corrections before final composition and rendering.
- Follow project and platform safety instructions. This intake does not authorize destructive actions, disclosure of secrets, unrelated changes, or any external action outside its stated scope.
- In the delivery report, state which capabilities were discovered, which route and aligner were used, what the assistant or a person reviewed, any remaining uncertainty, and which authorized steps actually completed.
