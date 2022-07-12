/**
 * This store handles (de)serializing between parameter JSON and `Field` class instances,
 * and sets up reactions for updating the necessary form on the page for POSTing the parameter data
 */

import { makeObservable, observable, action, reaction, toJS } from "mobx";
import { debounce } from "debounce";
import {
    dispatchDatapaneEvent,
    jsonParseIfStr,
    noUndefinedVals,
    onAlpineReady,
} from "./utils";
import * as f from "./fields";
import { Param, SerializedObject } from "./types";
import { EventType } from "../../../shared/types";

type FieldTest = {
    // use `any` instead of f.Field because typescript doesn't support
    // instantiating an unknown derived class that has an abstract base class (i.e. `new _class()`)
    // TODO - is this an anti-pattern? Seems that typescript should allow this otherwise
    class_: any;
    test: (param: any) => boolean;
    opts?: any;
};

const DEBOUNCE_MS = 400;

export class ParamsStore {
    public fields: f.Field[] = [];
    public serialized: SerializedObject = [];
    public disableFileFields = false;

    public constructor() {
        makeObservable(this, {
            fields: observable,
            serialized: observable,
            disableFileFields: observable,
            serialize: action,
        });
        this.setParamsChangeReaction();
        this.serialize = debounce(this.serialize, DEBOUNCE_MS);
    }

    public load(
        paramsJson: Param[],
        updatedFields: Param[],
        isSchedule?: boolean
    ): f.Field[] {
        /**
         * Performs the deserialization and necessary side effects on initial loading of the params JSON data
         */
        updatedFields &&
            this.setDefaults(paramsJson, jsonParseIfStr(updatedFields));
        this.fields = observable.array(ParamsStore.deserialize(paramsJson));
        this.disableFileFields = isSchedule || false;
        ParamsStore.setAlpineStore(paramsJson, this.disableFileFields);
        return this.fields;
    }

    public serialize(): SerializedObject {
        /**
         * Serializes the `fields` array into a form that can be POSTed to the server
         */
        const filtered = this.fields
            .map((field) => field.serialize())
            .filter((s) => noUndefinedVals(s));

        // Merge all fields into a single object
        this.serialized = filtered.reduce(
            (acc, curr) => ({ ...acc, ...curr }),
            {}
        );
        return this.serialized;
    }

    public static deserialize(params: Param[]): f.Field[] {
        /**
         * Deserializes an array of `Param` JSON objects into render-able `Field` instances
         */
        return params.map((param: any) => {
            const fieldTest:
                | FieldTest
                | undefined = ParamsStore.fieldMap.find((f) => f.test(param));
            if (fieldTest) {
                const { class_, opts } = fieldTest;
                return new class_(param, opts);
            } else {
                throw `Couldn't deserialize from JSON ${JSON.stringify(param)}`;
            }
        });
    }

    private setParamsChangeReaction() {
        /**
         * Updates the serialized object whenever the deserialized params change
         */
        reaction(
            () => toJS(this.fields),
            () => this.serialize()
        );
    }

    private setDefaults(paramsJson: Param[], updatedFields: Param[]) {
        /**
         * Updates params in-place with existing changes in a schedule (only used for scheduling)
         */
        paramsJson.forEach((field: any, idx: number) => {
            // set the default param field to the schedule's existing field values if available
            if (updatedFields[field.name]) {
                paramsJson[idx].default = updatedFields[field.name];
            }
        });
    }

    private static setAlpineStore(paramsJson: Param[], isSchedule: boolean) {
        /**
         * Disables schedules for params with required file fields
         */
        onAlpineReady(() => {
            const scheduleDisabled =
                isSchedule &&
                paramsJson.some((p) => p.type === "file" && p.required);
            dispatchDatapaneEvent(
                EventType.SCHEDULE_DISABLED,
                scheduleDisabled
            );
        });
    }

    public static fieldMap: FieldTest[] =
        /**
         * class_: The deserialized class that maps to a param
         * test: Function that returns true if the param should deserialize into the associated `class_`
         * opts: Additional metadata to be passed into the class
         */
        [
            {
                class_: f.InputIntFieldModel,
                test: (p) =>
                    p.type === "integer" &&
                    (p.min === undefined || p.max === undefined),
            },
            {
                class_: f.RangeIntFieldModel,
                test: (p) => p.type === "integer",
            },
            {
                class_: f.FloatFieldModel,
                test: (p) => p.type === "float",
            },
            {
                class_: f.TemporalFieldModel,
                test: (p) => p.type === "datetime",
                opts: {
                    timeFormat: "YYYY-MM-DDTHH:mm:ss",
                    type: "datetime-local",
                },
            },
            {
                class_: f.TemporalFieldModel,
                test: (p) => p.type === "date",
                opts: { timeFormat: "YYYY-MM-DD", type: "date" },
            },
            {
                class_: f.TemporalFieldModel,
                test: (p) => p.type === "time",
                opts: { timeFormat: "HH:mm:ss", type: "time" },
            },
            {
                class_: f.ListFieldModel,
                test: (p) => p.type === "list" && !p.choices,
            },
            {
                class_: f.ListFieldChoiceModel,
                test: (p) => p.type === "list",
            },
            {
                class_: f.EnumFieldModel,
                test: (p) => p.type === "enum",
            },
            {
                class_: f.StringFieldModel,
                test: (p) => p.type === "string",
            },
            {
                class_: f.BooleanFieldModel,
                test: (p) => p.type === "boolean",
            },
            {
                class_: f.FileFieldModel,
                test: (p) => p.type === "file",
            },
        ];
}

export const paramsStore = new ParamsStore();
