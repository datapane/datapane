import * as React from "react";

type Props = {
    msg: string;
    className: string;
};

export const ErrorPanel = (p: Props) => {
    return (
        <div
            className={`flex items-center p-2 text-sm min-w-0 sm:w-auto w-full bg-red-300 rounded ${p.className}`}
            data-cy="builder-error"
        >
            {p.msg}
        </div>
    );
};

ErrorPanel.defaultProps = {
    className: "",
};
