# Keeping your syllabus site up to date — automated version

Your repository now has two kinds of files:

| Location                        | What it is                                              | Do you touch it? |
|----------------------------------|----------------------------------------------------------|-------------------|
| `masters/eng102-5c-master.html`  | The editable master for 5C (with the control panel)       | **Yes — this is what you edit** |
| `masters/eng102-6f-master.html`  | The editable master for 6F                                | **Yes — this is what you edit** |
| `eng102-5c.html`, `eng102-6f.html` | The public pages students see                            | No — built automatically |
| `index.html`                     | The dashboard                                             | No — its "Last edit" dates update automatically |
| `scripts/build.py`               | The script that strips the panel and builds the pages     | No |
| `.github/workflows/build.yml`    | Tells GitHub to run that script automatically             | No |

**The rule of thumb: only ever edit files inside `masters/`.** Everything else is regenerated for you.

---

## One-time setup

1. Go to your repository on github.com.
2. Click **Add file → Upload files**.
3. Drag in the whole folder structure at once if your browser supports folder drag-and-drop (Chrome and Edge do) — it will preserve the `masters/`, `scripts/`, and `.github/workflows/` subfolders automatically.
   - If drag-and-drop only takes individual files for you, use **Add file → Create new file** instead, and type the full path (e.g. `masters/eng102-5c-master.html`) into the filename box — GitHub will create the folder for you. Repeat for each file.
4. Click **Commit changes**.
5. Click the **Actions** tab at the top of the repository. You should see a workflow run start automatically within a few seconds — it takes about 15–20 seconds to finish. A green checkmark means it worked.
6. Visit your live dashboard link. Both courses should be there, dated today.

---

## Updating a syllabus from now on

1. Open the master file you want to change — `masters/eng102-5c-master.html` or `masters/eng102-6f-master.html` — using the same on-page control panel you've been using, or ask me to make the change and hand you back the updated master.
2. On GitHub, click into that same file inside the `masters/` folder, click the pencil (edit) icon, and either paste in the new content or use **Add file → Upload files** to replace it with the new version — same filename.
3. Click **Commit changes**.
4. That's it. Within about 20 seconds, GitHub automatically:
   - strips the control panel out of the new master,
   - publishes the clean version to the matching public page,
   - and updates that course's "Last edit" date on the dashboard.
5. Refresh the live page to see it.

You can watch this happen under the **Actions** tab if you want to confirm it ran.

---

## Adding a third course later

1. Send me the syllabus content the way you have been. I'll build a new master styled to match, e.g. `masters/eng102-XX-master.html`.
2. I'll also hand you an updated `index.html` with a third row already added and tagged (`data-course="eng102-XX"`), so its date updates automatically too.
3. Upload both files into your repository the same way as above — the build script picks up any file in `masters/` automatically, no other setup needed.

---

## If something looks wrong

Check the **Actions** tab first. If the last run has a red X instead of a green check, click into it to see what failed — and send me a screenshot or the error text, and I'll help you fix it.
