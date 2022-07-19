import * as React from "react";

type DPButtonTheme = "light";

type Props = {
    icon?: string;
    children?: React.ReactNode;
    className?: string;
    intent: string;
    onClick: (e: React.MouseEvent<HTMLButtonElement>) => void;
    theme: DPButtonTheme;
    disabled?: boolean;
    dataCy?: string;
};

export const DPButton = (p: Props) => {
    return (
        <button
            type="button"
            className={`dp-btn-sm dp-btn-${p.intent} ${p.className} disabled:opacity-50`}
            onClick={p.onClick}
            disabled={p.disabled}
            data-cy={p.dataCy}
        >
            {p.icon && <i className={`mr-2 ${`fa ${p.icon}`}`} />}
            {p.children}
        </button>
    );
};

DPButton.defaultProps = {
    theme: "light",
    intent: "info",
    onClick: () => {},
};
