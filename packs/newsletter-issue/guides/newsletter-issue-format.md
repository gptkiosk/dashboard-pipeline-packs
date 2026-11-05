# Newsletter issue format

One issue is one folder: `issue/issue.md` plus `issue/meta.json` and pictures in `issue/img`.

- meta.json keys: title, subtitle (optional), preview_line, ai_disclosure ("ai_assisted" or "human"), header (file name or null), pictures (list of file, description).
- Title: under 70 characters, plain, no clickbait. Subtitle: one line under the title.
- Preview line: at most 90 characters. It is what an inbox shows after the subject, so it invites a reader in and never repeats the title.
- Body: Markdown with `##` headings, short paragraphs, one idea per section. 500 to 900 words unless the settings say otherwise.
- Header picture: 2:1 landscape. upubhub cuts it to 2:1 on upload, so keep the subject in the centre.
- Every picture has a description for the "Describe the picture" field in upubhub: what it shows, for readers who cannot see it. Screen readers and readers with images off rely on it, and upubhub will not publish the issue without it. 200 characters or fewer, plain words, no "image of", never the file name.
- Links are https only. Emails carry upubhub links, so author links belong on the newsletter page, not in the issue.
- Say plainly when art was made with AI; set ai_disclosure to match.
