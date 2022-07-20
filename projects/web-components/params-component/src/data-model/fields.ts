/**
 * Classes here represent deserialized field objects that contain their corresponding Vue components,
 * props and necessary transformations from the JSON parameter `properties`
 */

import { action, makeObservable, observable, toJS } from "mobx";
import { markRaw } from "vue";
import InputIntField from "../components/InputIntField.vue";
import RangeIntField from "../components/RangeIntField.vue";
import FloatField from "../components/FloatField.vue";
import DateTimeField from "../components/DateTimeField.vue";
import ListField from "../components/ListField.vue";
import ListFieldChoice from "../components/ListFieldChoice.vue";
import FileField from "../components/FileField.vue";
import EnumField from "../components/EnumField.vue";
import StringField from "../components/StringField.vue";
import BooleanField from "../components/BooleanField.vue";
import moment from "moment";
import {
    Param,
    ParamEnum,
    ParamListChoice,
    ParamNumeric,
    SerializedObject,
} from "./types";

export abstract class Field<T = any> {
    public component: any;
    public name: string;
    public helpText?: string;
    public required: boolean;
    public value: T;

    protected propNames: (keyof this)[] = [
        "value",
        "helpText",
        "required",
        "name",
        "setValue",
    ];

    private _props: any;

    public constructor(properties: Param, opts?: any) {
        makeObservable(this, {
            value: observable,
            setValue: action,
        });
        this.name = properties.name;
        this.value = properties.default;
        this.required = properties.required;
        this.helpText = properties.helpText;
    }

    public get props(): any {
        if (!this._props) {
            this._props = {};
            for (const propName of this.propNames) {
                const prop = this[propName];
                // a raw object should be passed to the view component rather than a mobx proxy
                this._props[propName] =
                    typeof prop === "object" ? toJS(prop) : prop;
            }
        }
        return this._props;
    }

    public serialize(): SerializedObject<T> {
        const obj: any = {};
        obj[this.name] = this.value;
        return obj;
    }

    public setValue = (v: any) => {
        this.value = v;
    };
}

export abstract class NumericField extends Field<number | undefined> {
    public serialize() {
        /**
         * Export value as number in JSON, or remove from params if missing or non-numeric
         */
        const obj: any = {};
        obj[this.name] =
            typeof this.value === "undefined" || isNaN(this.value)
                ? undefined
                : Number(this.value);
        return obj;
    }
}

export abstract class IntField extends NumericField {
    public min: number;
    public max: number;
    public step: number;

    public constructor(properties: ParamNumeric) {
        super(properties);
        this.min =
            properties.min === undefined ? -1 * Infinity : properties.min;
        this.max = properties.max === undefined ? Infinity : properties.max;
        this.step = properties.step || 1;
        this.propNames.push("min", "max", "step");
    }
}

export class InputIntFieldModel extends IntField {
    public component = markRaw(InputIntField);
}

export class RangeIntFieldModel extends IntField {
    public component = markRaw(RangeIntField);

    public constructor(properties: ParamNumeric) {
        super(properties);
        this.value =
            properties.default === undefined ? this.min : properties.default;
    }
}

export class FloatFieldModel extends NumericField {
    public component = markRaw(FloatField);
}

export class TemporalFieldModel extends Field<string | undefined> {
    public component = markRaw(DateTimeField);
    public type: string;

    public constructor(properties: Param<string | undefined>, opts: any) {
        super(properties);
        this.value = moment(properties.default).format(opts.timeFormat);
        this.type = opts.type;
        this.propNames.push("type");
    }
}

export class ListFieldModel extends Field<(string | number)[]> {
    public component = markRaw(ListField);

    public constructor(properties: Param<(string | number)[]>) {
        super(properties);
        this.value = properties.default || [];
    }
}

export class ListFieldChoiceModel extends Field<(string | number)[]> {
    public component = markRaw(ListFieldChoice);
    public choices: string[];

    public constructor(properties: ParamListChoice) {
        super(properties);
        this.value = properties.default || [];
        this.choices = properties.choices;
        this.propNames.push("choices");
    }
}

export class EnumFieldModel extends Field<string> {
    public component = markRaw(EnumField);
    public choices: string[];

    public constructor(properties: ParamEnum) {
        super(properties);
        this.value = properties.default || properties.choices[0];
        this.choices = properties.choices;
        this.propNames.push("choices");
    }
}

export class FileFieldModel extends Field<string | undefined> {
    public component = markRaw(FileField);
}

export class StringFieldModel extends Field<string | undefined> {
    public component = markRaw(StringField);

    public constructor(properties: any) {
        super(properties);
        this.value = properties.default || "";
    }
}

export class BooleanFieldModel extends Field<boolean> {
    public component = markRaw(BooleanField);

    public constructor(properties: Param<boolean>) {
        super(properties);
        this.value = properties.default || false;
    }
}

export class UnknownFieldModel extends Field {
    public constructor(properties: Param) {
        super(properties);
    }

    public serialize(): any {
        return {};
    }
}
