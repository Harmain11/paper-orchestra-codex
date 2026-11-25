# Interactive setup guide

`index.html` is a standalone, single-file website with locally executed JavaScript that generates copyable setup commands for the user's platform. It does not upload research materials or call external model APIs.

The page is deployable using GitHub Pages and the `.github/workflows/pages.yml` workflow, after the repository owner enables GitHub Pages using **Settings → Pages → GitHub Actions**.

The repository root `README.md` links to the expected Pages URL and also explains that the site is not live until Pages is enabled. Test locally by opening `index.html` in a modern browser.

The command builder is educational: it never executes commands. Upstream PaperOrchestra still requires an independently installed environment and, for manuscript generation, user-owned model-provider credentials.
