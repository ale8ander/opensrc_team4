# Contributing to Our Project

**We welcome contributions of all kinds!**

If you are having trouble with installation, please refer to [INSTALL.md](./docs/INSTALL.md).

## Areas you can contribute to

- [ ] Report bugs (e.g. crashes, incorrect gesture detection, compatibility issues)
- [ ] Suggest improvements to existing features or architecture
- [ ] Improve documentation or add helpful explanations for beginners
- [ ] Fix typos and grammar errors in code comments or documentation
- [ ] Implement new features (e.g. support for more gestures, dynamic gestures, multi-hand support)
- [ ] Refactor or optimize existing code (improve performance, readability, maintainability)
- *Feel free to refer to [ROADMAP.md](./docs/ROADMAP.md) as well*.

---

## Code Style Guide

- Please follow the [PEP 8 Python Style Guide](https://peps.python.org/pep-0008/).
- Whenever possible, add docstrings to your functions, classes, and modules to improve code readability and maintainability.

---

## How to Contribute

- Open an Issue
- `Fork` this repository
- Create a new branch: `git checkout -b feature/your-feature-name (or issue#)`
- Commit your changes: `git commit -m "Add feature xyz"`
- Push to your forked repository: `git push origin feature/your-feature-name`
- Open a Pull Request (PR) to the main repository

### Contribution Process (Detailed)

#### 1. Open an Issue

- Please create a `GitHub Issue` first.
- Clearly describe what you would like to contribute ***in detail***.
  - You can explain it fully in the Issue and simply link it in your PR later.
  - *The more detailed your description is, the lower the risk of rejection.*

#### 2. Fork and Create a Branch

- Fork this project.
- Clone your forked repository to your local machine and create a new branch:

```bash
git clone {forked repository URL}
cd {repository folder}
git checkout -b feature/issue#-number
```

#### 3. Implement your changes

- Make the necessary changes or add new features.

#### 4. Commit your changes

- Follow the commit message style:
  - feat(issue#N): Add new feature

  - fix(issue#N): Fix bug in gesture recognition

  - docs(issue#N): Improve documentation

#### 5. Push to your forked repository

```bash
git push origin feature/issue#-number
```

#### 6. Open a Pull Request to the main repository

- Go to your forked repository on GitHub.

- Click `Compare & pull request`.
- Clearly describe the purpose of the PR and link the related Issue.
  - If the Issue already contains a detailed explanation, you may keep this section brief or omit it.
  - Please make sure to ***link the related Issue*** when opening the PR. (e.g. Closes #12).
- Add screenshots or logs if applicable.

---

## License

- This project is licensed under the MIT License.
- All contributions will be subject to this license.
