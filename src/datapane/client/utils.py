import click


class DPException(Exception):
    ...
    # def __str__(self):
    #     print(self.args[0])
    #     return super().__str__()


class IncompatibleVersionException(DPException):
    ...


class UnsupportedResourceException(DPException):
    ...


class InvalidToken(DPException):
    ...


def success_msg(msg: str):
    click.secho(msg, fg="green")


def failure_msg(msg: str, do_exit: bool = False):
    click.secho(msg, fg="red")
    if do_exit:
        ctx: click.Context = click.get_current_context(silent=True)
        if ctx:
            ctx.exit(2)
        else:
            exit(2)
