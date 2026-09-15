# Setting up the Claude Code agent on your own copy of this repo

## Fast path (recommended)

You need repository admin access.

1. Open a terminal with [Claude Code](https://claude.ai/code) installed, in a checkout of your repo.
2. Run `/install-github-app`.
3. Follow the prompts — this installs the Claude GitHub App on the repo, grants it Contents / Issues / Pull Requests read-write, and adds `ANTHROPIC_API_KEY` as a repository secret automatically.
4. Add `.github/workflows/claude.yml` (already present in this repo) if it isn't there yet.

That's the whole setup — the workflow file in this repo already matches what the installer expects.

## Manual path

If you don't have the Claude Code CLI handy, or want more control:

1. Go to [github.com/apps/claude](https://github.com/apps/claude) and install it on your repository.
2. Grant it `Contents`, `Issues`, and `Pull requests` read/write permissions.
3. In your repo's **Settings → Secrets and variables → Actions**, add a secret named `ANTHROPIC_API_KEY` with a valid Anthropic API key (get one from [console.anthropic.com](https://console.anthropic.com)).
4. Confirm `.github/workflows/claude.yml` is present (it is, in this repo).

## Using AWS Bedrock / Google Vertex / Microsoft Foundry instead

The action supports these as alternatives to a direct `ANTHROPIC_API_KEY`. See the action's own [cloud-providers.md](https://github.com/anthropics/claude-code-action/blob/main/docs/cloud-providers.md) for the exact `use_bedrock` / `use_vertex` inputs — swap the relevant block into `.github/workflows/claude.yml`.

## Trying it out

1. Open an issue using the **New pizza term** template — e.g. propose "Hawaiian Pizza."
2. Comment `@claude handle issue #<N>` (or assign the issue to the `claude` bot user, or add the `claude` label — the workflow watches all three).
3. Check the **Actions** tab for the running job, then the **Pull requests** tab once it finishes.

## Troubleshooting

- **Action doesn't trigger**: confirm the GitHub App is installed on *this* repo specifically (not just your account), and that the comment/assignment matches one of the three triggers in `.github/workflows/claude.yml`.
- **`robot: command not found` in the agent's own commands**: the workflow installs ROBOT as a build step before invoking Claude; if you changed the runner image, make sure that install step still runs.
- **PR opened but `robot reason` wasn't actually run**: check the PR body — the template's checklist should reflect real output, not an assumed pass. If it looks templated rather than genuine, that's worth flagging as a bug in `CLAUDE.md`'s verification gate.
