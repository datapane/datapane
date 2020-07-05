# Copyright 2020 StackHut Limited (trading as Datapane)
# SPDX-License-Identifier: Apache-2.0

from .commands import cli


def main():
    # NOTE - cli doesn't return
    cli()


if __name__ == "__main__":
    main()
