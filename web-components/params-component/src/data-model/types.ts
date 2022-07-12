export type Param<T = any> = {
    name: string;
    type: string;
    required: boolean;
    default?: T;
    helpText?: string;
};

export type ParamNumeric = Param<number | undefined> & {
    min?: number;
    max?: number;
    step?: number;
};

export type ParamListChoice = Param<(string | number)[]> & {
    choices: string[];
};

export type ParamEnum = Param<string> & {
    choices: string[];
};

export type SerializedObject<T = any> = { [key: string]: T };
