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

# Set env vars for your project
req env set BASE_URL https://api.example.com
req env set TOKEN abc123

# Use them in requests
req get {{BASE_URL}}/users --auth {{TOKEN}}

# Build a collection
req collection init
req collection add "List Users" -m GET -p /users
req collection add "Create User" -m POST -p /users -j '{"name":"test"}'

# Run the whole collection
req collection run --base {{BASE_URL}} --verbose

# Browse history
req history
req history search /users
```

---

## Commands

| Group | Commands |
|-------|---------|
| **Requests** | `get`, `post`, `put`, `patch`, `delete` |
| **Options** | `--auth token`, `--auth user:pass`, `--header`, `--query`, `--json`, `--data` |
| **Env** | `req env list`, `req env set KEY VAL`, `req env get KEY`, `req env delete KEY` |
| **Collection** | `init`, `add`, `ls`, `run` |
| **History** | `req history`, `req history search <term>`, `req history --clear` |

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

- [ ] `req test` — run test assertions against responses
- [ ] Request chaining — extract data from one response to the next
- [ ] Export to Postman / OpenAPI / curl
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

MIT © [GoDon](https://github.com/GODONG-DN)
