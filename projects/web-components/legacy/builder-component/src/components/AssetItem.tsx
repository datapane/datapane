import * as React from "react";
import { NamedBlock } from "../metadata";
import {
    ChartBarIcon,
    TableIcon,
    CollectionIcon,
    CodeIcon,
    TerminalIcon,
    MenuAlt2Icon,
    ReceiptTaxIcon,
    FilmIcon,
    VariableIcon,
    CubeIcon,
} from "@heroicons/react/solid";

const getIcon = (assetType: string): JSX.Element => {
    switch (assetType) {
        case "Plot":
            return <ChartBarIcon />;
        case "DataTable":
        case "Table":
            return <TableIcon />;
        case "HTML":
            return <CodeIcon />;
        case "Code":
            return <TerminalIcon />;
        case "Text":
            return <MenuAlt2Icon />;
        case "Select":
        case "Group":
            return <CollectionIcon />;
        case "BigNumber":
            return <ReceiptTaxIcon />;
        case "Embed":
            return <FilmIcon />;
        case "Formula":
            return <VariableIcon />;
        default:
            return <CubeIcon />;
    }
};

type Props = {
    asset: NamedBlock;
    onClick: () => void;
};

export const AssetItem = (p: Props) => {
    return (
        <li
            key={p.asset.name}
            className="relative"
            data-cy={`asset-item-${p.asset.name}`}
        >
            <div className="group block w-full aspect-w-10 aspect-h-7 rounded-lg bg-gray-100 focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-offset-gray-100 focus-within:ring-indigo-500 overflow-hidden">
                <div className="object-cover flex justify-center pointer-events-none group-hover:opacity-75 text-gray-300 p-8">
                    {getIcon(p.asset.tagName)}
                </div>
                <button
                    type="button"
                    className="absolute inset-0 focus:outline-none"
                    onClick={p.onClick}
                    data-cy={`button-asset-${p.asset.tagName}`}
                ></button>
            </div>
            <p className="mt-2 block text-sm font-medium text-gray-900 truncate pointer-events-none">
                {p.asset.name}
            </p>
            <p className="block text-sm font-medium text-gray-500 pointer-events-none">
                {" "}
                {p.asset.metadata.join(" • ")}
            </p>
        </li>
    );
};
