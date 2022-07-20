import * as React from "react";
import { useState } from "react";

export type Option = {
    name: string;
    id: string;
    onClick: () => void;
};

export type Section = {
    title?: string;
    options: Option[];
};

type Props = {
    name: string;
    sections: Section[];
    className?: string;
    orientation?: "left" | "right";
};

export const DPDropdown = (p: Props) => {
    const [open, setOpen] = useState(false);

    return (
        <div
            data-cy={`dropdown-${p.name.toLowerCase()}`}
            className={`relative inline-block text-left ${p.className}`}
            style={{ zIndex: 5 }}
        >
            <div>
                <button
                    type="button"
                    className="dp-btn-sm px-1 sm:px-2 sm:px-2 py-0"
                    id="options-menu"
                    onClick={() => setOpen(!open)}
                    onBlur={() => setTimeout(() => setOpen(false), 200)}
                >
                    {p.name}
                    <svg
                        className="-mr-1 ml-1 h-5 w-5"
                        xmlns="http://www.w3.org/2000/svg"
                        viewBox="0 0 20 20"
                        fill="currentColor"
                        aria-hidden="true"
                    >
                        <path
                            fillRule="evenodd"
                            d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
                            clipRule="evenodd"
                        />
                    </svg>
                </button>
            </div>
            <div
                className={`${!open ? "hidden" : ""} ${
                    p.orientation === "left"
                        ? "origin-top-left left-0"
                        : "origin-top-right right-0"
                }  absolute  w-56 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 divide-y divide-gray-100`}
                role="menu"
                aria-orientation="vertical"
                aria-labelledby="options-menu"
            >
                {p.sections.map((section, sectionIdx) => (
                    <div className="py-1" key={sectionIdx}>
                        {section.title && (
                            <div className="text-xs pl-2 py-2 font-semibold">
                                {section.title}
                            </div>
                        )}
                        {section.options.map((option, optionIdx) => (
                            <a
                                data-cy={`dropdown-option-${option.id}`}
                                id={option.id}
                                onClick={option.onClick}
                                className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 hover:text-gray-900 cursor-pointer"
                                key={`${sectionIdx}-${optionIdx}`}
                                role="menuitem"
                            >
                                {option.name}
                            </a>
                        ))}
                    </div>
                ))}
            </div>
        </div>
    );
};
