import Modal from "react-modal";
import React, { useContext } from "react";
import { BuilderProviderContext } from "../data-model/BuilderStore";
import { MobXProviderContext } from "mobx-react";
import { AssetsBar } from "./AssetsBar";
import { XIcon } from "@heroicons/react/outline";
type Props = {
    isOpen: boolean;
    close: () => void;
    insertAsset: () => any;
};

const customStyles = {
    content: {
        top: "50%",
        left: "50%",
        right: "auto",
        bottom: "auto",
        marginRight: "-50%",
        borderRadius: "0.5rem",
        paddingTop: "0px",
        transform: "translate(-50%, -50%)",
        width: "64rem",
        height: "36rem",
        background: "white",
    },
    overlay: {
        zIndex: 1000,
        background: "rgba(107, 114, 128, 0.75)",
    },
};

export const PythonAssetsModal = (p: Props) => {
    const { store } = useContext<BuilderProviderContext>(MobXProviderContext);

    const onEditorChange = (val: string) => {
        store.editorContent = val;

        /* Unset on save */
        if (!window.onbeforeunload) {
            window.onbeforeunload = function () {
                return true;
            };
        }

        p.close();
    };

    return (
        <Modal
            isOpen={p.isOpen}
            onRequestClose={p.close}
            style={customStyles}
            ariaHideApp={false}
        >
            <AssetsBar
                closeModal={p.close}
                updateEditor={onEditorChange}
                assets={store.assets}
                saving={store.saving}
                refreshing={store.refreshingAssets}
            />
            <div className="hidden sm:block absolute top-0 right-0 pt-4 pr-4">
                <button
                    onClick={p.close}
                    type="button"
                    className="bg-white rounded-md text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                    <XIcon className="h-6 w-6" />
                </button>
            </div>
        </Modal>
    );
};
