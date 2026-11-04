# Where issue art comes from

Pick one source per issue from the settings.

- fal.ai in Media studio: the agent writes `media/slots.json` (placement, alt text, size, prompt, estimate). A person approves the shown spend and runs Generate in the project Media tab, then picks and publishes the candidates. Agents never hold the fal key.
- Codex images: the agent writes `media/prompts.md`, one numbered prompt per picture with its file name and size. A person makes each image in Codex, saves it into `media/incoming` under the file name given, and approves it.
- Existing images only: a person places files in `media/incoming`; the agent checks size, alt text and fit with the style kit.

Either way the agent then copies approved files into `issue/img` and references them from the issue. A drawn placeholder is never evidence that final art shipped.
