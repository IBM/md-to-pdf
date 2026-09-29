<!--
Copyright IBM Corp. 2025, 2026
SPDX-License-Identifier: Apache-2.0
Created with IBM Bob (https://bob.ibm.com)
-->

# Contributing

Our project welcomes external contributions. If you have an itch, please feel
free to scratch it.

To contribute code or documentation, please submit a
[pull request](https://github.com/ibm/md-to-pdf/pulls).

A good way to familiarize yourself with the codebase and contribution process is
to look for and tackle low-hanging fruit in the
[issue tracker](https://github.com/ibm/md-to-pdf/issues).
Before embarking on a more ambitious contribution, please quickly
[get in touch](#communication) with us.

**Note: We appreciate your effort, and want to avoid a situation where a
contribution requires extensive rework (by you or by us), sits in backlog for a
long time, or cannot be accepted at all!**

## Proposing new features

Please [raise an issue](https://github.com/ibm/md-to-pdf/issues) before sending
a pull request so the feature can be discussed. This avoids you investing time
in a feature the project maintainers may not accept.

## Fixing bugs

Please [raise an issue](https://github.com/ibm/md-to-pdf/issues) before sending
a pull request so the bug can be tracked.

## Merge approval

The project maintainers use LGTM (Looks Good To Me) in comments on the code
review to indicate acceptance. A change requires LGTM from one of the
maintainers listed in [MAINTAINERS.md](MAINTAINERS.md).

## Legal

Each source file must include a license header for the Apache Software License
2.0. Using the SPDX format is the simplest approach:

```python
# Copyright IBM Corp. 2025, 2026
# SPDX-License-Identifier: Apache-2.0
```

We use the [Developer's Certificate of Origin 1.1 (DCO)](https://github.com/hyperledger/fabric/blob/master/docs/source/DCO1.1.txt)
to manage code contributions. When submitting a patch, include a sign-off
statement in your commit message:

```
Signed-off-by: Your Name <your.email@example.com>
```

Add this automatically with:

```bash
git commit -s
```

## Communication

Please feel free to open a [GitHub Discussion](https://github.com/ibm/md-to-pdf/discussions)
or create an [issue](https://github.com/ibm/md-to-pdf/issues).

## Setup

```bash
git clone https://github.com/ibm/md-to-pdf.git
cd md-to-pdf
uv venv
uv pip install -e ".[dev]"
```

## Coding style guidelines

- Follow PEP 8
- Include SPDX license header in every new source file
- Keep functions small and focused
