import { Block, BlockFigure, Elem } from "./leaf-blocks";
import { markRaw } from "vue";
import VRangeField from "../../components/controls/RangeField.vue";
import VInputField from "../../components/controls/InputField.vue";
import VTagsField from "../../components/controls/TagsField.vue";
import VSwitchField from "../../components/controls/SwitchField.vue";
import VMultiChoiceField from "../../components/controls/MultiChoiceField.vue";
import VFileField from "../../components/controls/FileField.vue";
import VDateTimeField from "../../components/controls/DateTimeField.vue";
import VSelectField from "../../components/controls/SelectField.vue";
import moment from "moment";
import he from "he";

const parseJsonProp = (json: string): Record<string, unknown> | string[] =>
    /**
     * Decode HTML entities and parse as JSON,
     * e.g. `"[&quot;foo&qout;]"` -> `["foo"]`
     */
    JSON.parse(he.decode(json));

export abstract class ControlsField extends Block {
    public constructor(elem: Elem, figure: BlockFigure) {
        super(elem, figure); // TODO -- `figure` is unused, should use new base class?
        const { helpText, name, required, initial, label } = elem.attributes;
        this.componentProps = {
            ...this.componentProps,
            helpText,
            name,
            label,
            initial,
            required: required ? JSON.parse(required) : undefined,
        };
    }
}

export class RangeField extends ControlsField {
    public component = markRaw(VRangeField);

    public constructor(elem: Elem, figure: BlockFigure) {
        super(elem, figure);
        const { min, max, step, initial } = elem.attributes;
        this.componentProps = {
            ...this.componentProps,
            min: +min,
            max: +max,
            step: +step,
            initial: +initial,
        };
    }
}

export class InputField extends ControlsField {
    public component = markRaw(VInputField);

    public constructor(elem: Elem, figure: BlockFigure) {
        super(elem, figure);
        this.componentProps = { ...this.componentProps };
    }
}

export class TagsField extends ControlsField {
    public component = markRaw(VTagsField);

    public constructor(elem: Elem, figure: BlockFigure) {
        super(elem, figure);
        const { initial } = elem.attributes;
        this.componentProps = {
            ...this.componentProps,
            initial: initial ? parseJsonProp(initial) : [],
        };
    }
}

export class MultiChoiceField extends ControlsField {
    public component = markRaw(VMultiChoiceField);

    public constructor(elem: Elem, figure: BlockFigure) {
        super(elem, figure);
        const { initial, choices } = elem.attributes;
        this.componentProps = {
            ...this.componentProps,
            choices: JSON.parse(choices),
            initial: initial ? parseJsonProp(initial) : [],
        };
    }
}

export class FileField extends ControlsField {
    public component = markRaw(VFileField);

    public constructor(elem: Elem, figure: BlockFigure) {
        super(elem, figure);
    }
}

export class TemporalField extends ControlsField {
    public component = markRaw(VDateTimeField);

    public constructor(elem: Elem, figure: BlockFigure, opts?: any) {
        super(elem, figure);
        const { initial } = elem.attributes;
        const { timeFormat, type } = opts;
        this.componentProps = {
            ...this.componentProps,
            // `moment(undefined)` resolves to current date
            initial: moment(initial).format(timeFormat),
            type,
        };
    }
}

export class SelectField extends ControlsField {
    public component = markRaw(VSelectField);
    public choices: string[];

    public constructor(elem: Elem, figure: BlockFigure) {
        super(elem, figure);
        const { initial, choices } = elem.attributes;
        this.choices = parseJsonProp(choices) as string[];

        this.componentProps = {
            ...this.componentProps,
            choices: this.choices,
            initial: initial || this.choices[0],
        };
    }
}

export class SwitchField extends ControlsField {
    public component = markRaw(VSwitchField);

    public constructor(elem: Elem, figure: BlockFigure) {
        super(elem, figure);
        const { initial } = elem.attributes;
        this.componentProps = {
            ...this.componentProps,
            initial: initial ? JSON.parse(initial) : false,
        };
    }
}
