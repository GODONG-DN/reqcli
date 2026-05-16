# Req

> **Terminal API client** — like Postman, but in your terminal.
> Make requests, manage env vars, run collections, all from the command line.

<p align="center">
  <img src="https://img.shields.io/github/license/GODONG-DN/reqcli" alt="License">
  <img src="https://img.shields.io/github/actions/workflow/status/GODONG-DN/reqcli/ci.yml?branch=master" alt="CI">
</p>

---

## Why Req?

Postman is a GUI. curl is a one-liner. httpie is pretty but stateless. **Req** sits in the middle — it lets you:

- **Make requests** with beautiful syntax-highlighted output
- **Save env vars** per-project, with `{{variable}}` substitution
- **Build collections** of requests, stored as JSON (git-friendly!)
- **Run & test** your entire collection with one command
- **Browse history** and replay past requests

Output is color-coded, JSON is auto-formatted, and everything is local — no account, no cloud.

---

## Quickstart

```bash
pip install reqcli
```

```bash
# Simple GET
req get https://api.github.com/repos/GODONG-DN/reqcli

# With auth
req get https://api.github.com/user --auth $GITHUB_TOKEN

# POST JSON
req post https://jsonplaceholder.typicode.com/posts -j '{"title":"hello"}'

# Silent mode (just the body)
req get https://jsonplaceholder.typicode.com/posts/1 -s

# Export as curl
req get https://api.example.com/users -H "Authorization: Bearer abc" -e

# Set env vars for your project
req env set BASE_URL https://api.example.com
req env set TOKEN abc123

# Use them in requests
req get {{BASE_URL}}/users --auth {{TOKEN}}

# Import from .env file
req env load .env

# Request chaining — extract and reuse
req post {{BASE_URL}}/login -j '{"user":"me"}' -x token --silent
req get {{BASE_URL}}/profile --auth '{{$token}}' -s

# Build a collection
req collection init
req collection add "List Users" -m GET -p /users
req collection add "Create User" -m POST -p /users -j '{"name":"test"}'

# Run the whole collection
req collection run --base {{BASE_URL}}

# Browse history
req history
```

---

## Commands

| Group | Commands |
|-------|---------|
| **Requests** | `get`, `post`, `put`, `patch`, `delete` |
| **Options** | `--auth token`, `--auth user:pass`, `--header`, `--query`, `--json`, `--data`, `--silent`, `--export`, `--extract key` |
| **Env** | `list`, `set KEY VAL`, `get KEY`, `delete KEY`, `load .env`, `export .env` |
| **State** | `req state` (view extracted values for chaining) |
| **Collection** | `init`, `add`, `ls`, `run` |
| **History** | `req history`, `req history search`, `req history --clear` |

---

## Data storage

Everything lives in `.req/` in your project root:

```
.req/
├── env.json         # your variables (you can git-ignore this)
├── collection.json  # your request collection (commit this!)
└── history.json     # recent requests
```

---

## Roadmap

- [x] `.env` file load/export
- [x] Request chaining with `--extract` and `{{$key}}`
- [ ] `req test` — run test assertions against responses
- [ ] Export to Postman / OpenAPI
- [ ] Scriptable pre-request hooks
- [ ] Interactive TUI browser for collections
- [ ] GraphQL support

---

## Contributing

```bash
git clone https://github.com/GODONG-DN/reqcli.git
cd req
pip install -e ".[dev]"
pytest
```

---

## License

Open-source under the MIT License. © [GoDon](https://github.com/GODONG-DN)
