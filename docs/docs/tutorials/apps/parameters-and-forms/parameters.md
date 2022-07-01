---
description: Parameters customise your script and can turn it into a web form
---

# Parameters

### Parameter Options

When you define your list of parameters, all can include the following options.

| Field        | Required | Description                                                                                                                         |
| ------------ | -------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| name         | True     | The name of the parameter. This must be a combination of lower case letters, numbers, and dashes and must be unique to your script. |
| type         | True     | The type of the parameter (see options below)                                                                                       |
| description  | False    | A description which is presented to the user when they run your form.                                                               |
| required     | False    | Whether your parameter is required or optional. Defaults to true.                                                                   |
| default      | False    | A default value for your parameter.                                                                                                 |

### Parameter Form Fields

The `type` of your parameter and other settings dictates how it is presented in your form. Datapane supports the following form fields.

| **Form Field**       | **`type`** | Extra options                                                | **Default value**         |
| -------------------- | ---------- | ------------------------------------------------------------ | ------------------------- |
| Text input           | `string`   |                                                              | `””`                      |
| Slider               | `integer`  | Both `min` and`max`properties set.                           | `min` value               |
| Integer input        | `integer`  | One of `min`/`max` not set                                   | `undefined`               |
| Float input          | `float`    |                                                              | `undefined`               |
| Boolean input        | `boolean`  |                                                              | `false`                   |
| Dropdown             | `enum`     |                                                              | The first choice supplied |
| Date picker          | `date`     |                                                              | `undefined`               |
| Time picker          | `time`     |                                                              | `undefined`               |
| Date and time picker | `datetime` |                                                              | `undefined`               |
| List Input           | `list`     | If provided with no `choices`                                | `[]`                      |
| Multi Select Input   | `list`     | If provided with `choices`: an array of strings and numbers. | `[]`                      |
