# How to contribute

Become one of the contributors to this project! We thrive to build a welcoming and open community for anyone who wants to use the project or contribute to it. To help us create a safe and positive community experience for all, we require all participants to adhere to the [Code of Conduct](https://github.com/dell/ansible-objectscale/blob/main/docs/CODE_OF_CONDUCT.md).

## Table of contents

* [Become a contributor](#Become-a-contributor)
* [Submitting issues](#Submitting-issues)
* [Triage issues](#Triage-issues)
* [Your first contribution](#Your-first-contribution)
* [Branching](#Branching)
* [Signing your commits](#Signing-your-commits)
* [Pull requests](#Pull-requests)
* [Code reviews](#Code-reviews)
* [TODOs in the code](#TODOs-in-the-code)

## Become a contributor

You can contribute to this project in several ways. Here are some examples:

* Contribute to the Ansible modules for Dell ObjectScale documentation and codebase.
* Report and triage bugs.
* Feature requests.
* Write technical documentation and blog posts, for users and contributors.
* Help others by answering questions about this project.

## Submitting issues

All issues related to Ansible modules for Dell ObjectScale, regardless of the service/repository the issue belongs to (see table above), should be submitted [here](https://github.com/dell/ansible-objectscale/issues). Issues will be triaged and labels will be used to indicate the type of issue. This section outlines the types of issues that can be submitted.  

### Report bugs

We aim to track and document everything related to Ansible modules for Dell ObjectScale via the Issues page. The code and documentation are released with no warranties or SLAs and are intended to be supported through a community driven process.

Before submitting a new issue, make sure someone hasn't already reported the problem. Look through the [existing issues](https://github.com/dell/ansible-objectscale/issues) for similar issues.

Report a bug by submitting a [bug report](https://github.com/dell/ansible-objectscale/issues/new?labels=type%2Fbug%2C+needs-triage&template=bug_report.md&title=%5BBUG%5D%3A). Make sure that you provide as much information as possible on how to reproduce the bug.

When opening a Bug please include this information to help with debugging:

1. Version of relevant software: this software, Ansible, Python, SDK, etc.
2. Details of the issue explaining the problem: what, when, where
3. The expected outcome that was not met (if any)
4. Supporting troubleshooting information. __Note: Do not provide private company information that could compromise your company's security.__

An Issue __must__ be created before submitting any pull request. Any pull request that is created should be linked to an Issue.

### Feature request

If you have an idea of how to improve this project, submit a [feature request](https://github.com/dell/ansible-objectscale/issues/new?labels=type%2Ffeature-request%2C+needs-triage&template=feature_request.md&title=%5BFEATURE%5D%3A).

## Branching

The main branch contains the latest stable release. All development work should happen in feature branches. Please follow the naming convention for branches:

* Feature branches: `usr/<username>/<feature-name>`
* Bugfix branches: `bugfix/<username>/<bug-description>`
* Hotfix branches: `hotfix/<username>/<hotfix-description>`

## Signing your commits

We require all commits to be signed. Please configure your Git client to sign commits:

```bash
git config --global commit.gpgsign true
git config --global user.signingkey YOUR_GPG_KEY_ID
```

## Pull requests

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

Make sure your pull request:
- Has a descriptive title
- References the related issue
- Includes tests
- Passes all CI checks
- Maintains code coverage

## Code reviews

All code changes must be reviewed by at least one maintainer. Reviewers will check for:
- Code quality
- Test coverage
- Documentation
- Security considerations

## TODOs in the code

If you need to leave a TODO in the code, please include:
- A clear description of what needs to be done
- The issue number (if applicable)
- Your name or initials

Example:
```python
# TODO: Add error handling for edge cases (Issue #123) - RA
```
